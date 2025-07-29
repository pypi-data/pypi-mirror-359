_PY = _PY
local fmt = string.format
local bundled = require("plua.bundled_files")
local json = require("plua.json")
local class = require("plua.class")
local net = require("plua.net")
__TAG = "<font color='light_blue'>PLUA</font>"

local DEVICEID = 5555-1

---@class Emulator
Emulator = {}
class 'Emulator'
function Emulator:__init(plua)
  self.DIR = {}  -- deviceId -> { device = {}, path="..", qa=...}
  self.lib = plua
  self.lib.userTime = os.time
  self.lib.userDate = os.date
  self.offline = false
  
  self.EVENT = {}
  self.debugFlag = false

  local api = {}
  function api.get(path) return self:API_CALL("GET", path) end
  function api.post(path, data) return self:API_CALL("POST", path, data) end
  function api.put(path, data) return self:API_CALL("PUT", path, data) end
  function api.delete(path) return self:API_CALL("DELETE", path) end
  self.lib.api = api
  
  local hc3api = {}
  function hc3api.get(path) return self:HC3_CALL("GET", path) end
  function hc3api.post(path, data) return self:HC3_CALL("POST", path, data) end
  function hc3api.put(path, data) return self:HC3_CALL("PUT", path, data) end
  function hc3api.delete(path) return self:HC3_CALL("DELETE", path) end
  self.lib.hc3api = hc3api
  
  self.lib.loadLib("fibaro_api",self)
  self.lib.ui = self.lib.loadLib("ui",self)
end

function Emulator:registerDevice(info)
  if info.device.id == nil then DEVICEID = DEVICEID + 1; info.device.id = DEVICEID end
  self.DIR[info.device.id] = { 
    device = info.device, files = info.files, env = info.env, headers = info.headers,
    UI = info.UI,
  }
end

local function validate(str,typ,key)
  local stat,val = pcall(function() return load("return "..str)() end)
  if not stat then error(fmt("Invalid header %s: %s",key,str)) end
  if typ and type(val) ~= typ then 
    error(fmt("Invalid header %s: expected %s, got %s",key,typ,type(val)))
  end
  return val
end

local headerKeys = {}
function headerKeys.name(str,info) info.name = str end
function headerKeys.type(str,info) info.type = str end
function headerKeys.state(str,info) info.state = str end
function headerKeys.proxy(str,info,k) info.proxy = validate(str,"boolean",k) end
function headerKeys.proxy_port(str,info,k) info.proxy_port = validate(str,"number",k) end
function headerKeys.offline(str,info,k) info.offline = validate(str,"boolean",k) end
function headerKeys.time(str,info,k) info.time = str end
function headerKeys.uid(str,info,k) info.version =str end
function headerKeys.manufacturer(str,info) info.manufacturer = str end
function headerKeys.model(str,info) info.model = str end
function headerKeys.role(str,info) info.role = str end
function headerKeys.description(str,info) info.description = str end
function headerKeys.latitude(str,info,k) info.latitude = validate(str,"number",k) end
function headerKeys.longitude(str,info,k) info.longitude = validate(str,"number",k) end
function headerKeys.debug(str,info,k) info.debug = validate(str,"boolean",k) end
function headerKeys.save(str,info) info.save = str end
function headerKeys.interfaces(str,info) info.interfaces = str end
function headerKeys.var(str,info,k) 
  local name,value = str:match("^([%w_]+)%s*=%s*(.+)$")
  assert(name,"Invalid var header: "..str)
  info.vars[#info.vars+1] = {name=name,value=validate(value,nil,k)}
end
function headerKeys.u(str,info) info._UI[#info._UI+1] = str end
function headerKeys.file(str,info)
  local path,name = str:match("^([^,]+),(.+)$")
  assert(path,"Invalid file header: "..str)
  if _PY.file_exists(path) then
    info.files[name] = {path = path, content = nil }
  else
    error(fmt("File not found: '%s'",path))
  end
end

function Emulator:processHeaders(filename,content)
  local shortname = filename:match("([^/\\]+%.lua)")
  local name = shortname:match("(.+)%.lua")
  local headers = {
    name=name or "MyQA",
    type='com.fibaro.binarySwitch',
    files={},
    vars={},
    _UI={},
  }
  local code = "\n"..content
  code:gsub("\n%-%-%%%%([%w_]-):([^\n]*)",function(key,str) 
    str = str:match("^%s*(.-)%s*$") or str
    str = str:match("^(.*)%s* %-%- (.*)$") or str
    if headerKeys[key] then
      headerKeys[key](str,headers,key)
    else print(fmt("Unknown header key: '%s' - ignoring",key)) end 
  end)
  local UI = (nil or {}).UI or {} -- ToDo: extraHeaders
  for _,v in ipairs(headers._UI) do 
    local v0 = validate(v,"table","u")
    UI[#UI+1] = v0
    v0 = v0[1] and v0 or { v0 }
    for _,v1 in ipairs(v0) do
      --local ok,err = Type.UIelement(v1)
      --assert(ok, fmt("Bad UI element: %s - %s",v1,err))
    end
  end
  headers.UI = UI
  headers._UI = nil
  return content,headers
end

local function loadFile(env,path,name,content)
  if not content then
    local file = io.open(path, "r")
    assert(file, "Failed to open file: " .. path)
    content = file:read("*all")
    file:close()
  end
  local func, err = load(content, path, "t", env)
  if func then func() return true
  else error(err) end
end

function Emulator:loadResource(fname,parseJson)
  local file = io.open(fname, "r")
  assert(file, "Failed to open file: " .. fname)
  local content = file:read("*all")
  file:close()
  if parseJson then return json.decode(content) end
  return content
end

function Emulator:createUI(UI) -- Move to ui.lua ? 
  self.lib.ui.extendUI(UI)
  local uiCallbacks,viewLayout,uiView
  if UI and #UI > 0 then
    uiCallbacks,viewLayout,uiView = self.lib.ui.compileUI(UI)
  else
    viewLayout = json.decode([[{
        "$jason": {
          "body": {
            "header": {
              "style": { "height": "0" },
              "title": "quickApp_device_57"
            },
            "sections": { "items": [] }
          },
          "head": { "title": "quickApp_device_57" }
        }
      }
  ]])
    viewLayout['$jason']['body']['sections']['items'] = json.initArray({})
    uiView = json.initArray({})
    uiCallbacks = json.initArray({})
  end
  return uiCallbacks,viewLayout,uiView
end

local deviceTypes = nil

function Emulator:createInfoFromContent(filename,content)
  local info = {}
  local preprocessed,headers = self:processHeaders(filename,content)
  if deviceTypes == nil then deviceTypes = self:loadResource(bundled.get_lua_path().."/rsrsc/devices.json",true) end
  headers.type = headers.type or 'com.fibaro.binarySwitch'
  local dev = deviceTypes[headers.type]
  assert(dev,"Unknown device type: "..headers.type)
  if not headers.id then DEVICEID = DEVICEID + 1 end
  dev.id = headers.id or DEVICEID
  dev.name = headers.name or "MyQA"
  dev.enabled = true
  dev.visible = true
  info.device = dev
  info.files = headers.files or {}
  local props = dev.properties or {}
  props.quickAppVariables = headers.vars or {}
  props.quickAppUuid = headers.uid
  props.manufacturer = headers.manufacturer
  props.model = headers.model
  props.role = headers.role
  props.description = headers.description
  props.uiCallbacks,props.viewLayout,props.uiView = self:createUI(headers.UI or {})
  info.files.main = { path=filename, content=preprocessed }
  local specProps = {
    uid='quickAppUuid',manufacturer='manufacturer',
    mode='model',role='deviceRole',
    description='userDescription'
  }
  info.UI = headers.UI
  for _,prop in ipairs(specProps) do
    if headers[prop] then props[prop] = headers[prop] end
  end
  info.headers = headers
  return info
end

function Emulator:createInfoFromFile(filename)
  -- Read the file content
  local file = io.open(filename, "r")
  assert(file, "Failed to open file: " .. filename)
  local content = file:read("*all")
  file:close()
  return self:createInfoFromContent(filename,content)
end

function Emulator:startQA(id)
  local info = self.DIR[id]
  local env = info.env
  env.setTimeout(function()
    if env.QuickApp.onInit then
      env.quickApp = env.QuickApp(info.device)
    end
  end, 0)
end

function Emulator:restartQA(id)
  local info = self.DIR[id]
  self:INFO("Restarting QA",id, "in 4s")
  info.env.setTimeout(function()
    self:loadQA(info)
    self:startQA(id)
  end,4000)
end

local stdLua = { 
  "string", "table", "math", "os", "io", 
  "package", "coroutine", "debug", "require",
  "setTimeout", "clearTimeout", "setInterval", "clearInterval",
  "setmetatable", "getmetatable", "rawget", "rawset", "rawlen",
  "next", "pairs", "ipairs", "type", "tonumber", "tostring", "pcall", "xpcall",
  "error", "assert", "select", "unpack", "load", "loadstring", "loadfile", "dofile",
  "print",
}

function Emulator:loadQA(info)
  -- Load and execute included files + main file
  local env = { 
    fibaro = { plua = self }, net = net, json = json, api = self.lib.api,
    __fibaro_add_debug_message = self.lib.__fibaro_add_debug_message, _PY = _PY,
  }
  for _,name in ipairs(stdLua) do env[name] = _G[name] end
  
  info.env = env
  local luapath = bundled.get_lua_path()
  loadfile(luapath.."/plua/fibaro.lua","t",env)()
  loadfile(luapath.."/plua/quickapp.lua","t",env)()
  env.plugin.mainDeviceId = info.device.id
  for name,f in pairs(info.files) do
    if name ~= 'main' then loadFile(env,f.path,name,f.content) end
  end
  loadFile(env,info.files.main.path,'main',info.files.main.content)
end

function Emulator:loadMainFile(filename)
  if not (filename and filename:match("%.lua$")) then return false end
  
  local info = self:createInfoFromFile(filename)
  if info.headers.offline then
    self:DEBUG("Offline mode")
  end
  
  self:loadQA(info)

  self:registerDevice(info)
  
  if info.headers.offline then
    -- If main files has offline directive, setup offline routes
    self.offline = true
    self.lib.loadLib("offline",self)
    self.lib.setupOfflineRoutes()
  end
  
  self:startQA(info.device.id)
end

function Emulator:API_CALL(method, path, data)
  local api_url = self.lib.api_url
  -- Call _PY.fibaroapi directly to avoid HTTP request blocking
  self:DEBUG("API: " .. api_url .. "/api" .. path)
  local result, status_code = _PY.fibaroapi(method, "/api" .. path, data)
  
  -- fibaroapi now handles redirects internally and always returns {data, status_code}
  return result, status_code or 200, {}
end

function Emulator:HC3_CALL(method, path, data, redirect)
  
  if not self.lib.hc3_creds then
    self:ERROR("HC3 credentials not configured")
    return {error = "HC3 credentials not configured"}, 401
  end
  
  -- Construct the external URL with the full path (including query parameters)
  local external_url = self.lib.hc3_url..path
  if redirect then
    self:DEBUG("Redirect to: " .. external_url)
  else
    self:DEBUG("HC3 api: " .. external_url)
  end
  
  -- Prepare request data
  local request_data = {
    url = external_url,
    method = method,
    headers = {
      ["Authorization"] = self.lib.hc3_creds,
      ["Content-Type"] = "application/json"
    }
  }
  
  -- Add body for POST/PUT requests
  if data and (method == "POST" or method == "PUT") then
    if type(data) == "table" then
      request_data.body = json.encode(data)
    else
      request_data.body = tostring(data)
    end
  end
  
  -- Make the HTTP request
  local http_result = _PY.http_request_sync(request_data)
  
  -- Parse the response
  local response_body = http_result.body
  local response_data = nil
  
  if response_body and response_body ~= "" then
    local success, parsed = pcall(json.decode, response_body)
    if success then
      response_data = parsed
    else
      self:ERROR("JSON parse error: " .. tostring(parsed))
      response_data = response_body
    end
  else
    self:DEBUG("Empty response body")
    response_data = {}
  end
  
  -- Return consistent format: {data, status_code}
  return response_data, http_result.code or 200
end

local pollStarted = false
function Emulator:startRefreshStatesPolling()
  if not (self.offline or pollStarted) then
    pollStarted = true
    local result = _PY.pollRefreshStates(0, self.lib.hc3_url.."/api/refreshStates?last=", {
      headers = {Authorization = self.lib.hc3_creds}
    })
  end
end

function Emulator:getRefreshStates(last) return _PY.getEvents(last) end

function Emulator:refreshEvent(typ,data) _PY.addEvent(json.encode({type=typ,data=data})) end

function Emulator:DEBUG(...) if self.debugFlag then print(...) end end
function Emulator:INFO(...) __fibaro_add_debug_message(__TAG, self.lib.logStr(...), "INFO", false) end 
function Emulator:ERROR(...) printErr(...) end

return Emulator