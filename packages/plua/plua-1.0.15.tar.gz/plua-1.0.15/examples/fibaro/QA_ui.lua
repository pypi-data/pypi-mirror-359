--%%name:UItest
--%%type:com.fibaro.binarySwitch
--%%debug:false
--%% offline:true

--%%u:{label="lbl1",text="Hello Tue Jul 1 06_34:53 2025"}
--%%u:{{button="button_ID_6_1",text="Btn 1",visible=true,onLongPressDown="",onLongPressReleased="",onReleased="testBtn1"},{button="button_ID_6_2",text="Btn 2",visible=true,onLongPressDown="",onLongPressReleased="",onReleased="testBtn2"},{button="button_ID_6_3",text="Btn 3",visible=true,onLongPressDown="",onLongPressReleased="",onReleased="testBtn3"},{button="button_ID_6_4",text="Btn 5",visible=true,onLongPressDown="",onLongPressReleased="",onReleased="testBtn5"}}
--%%u:{switch="btn2",text="Btn2",value="false",visible=true,onReleased="mySwitch"}
--%%u:{slider="slider1",text="",min="0",max="100",visible=true,onChanged="mySlider"}
--%%u:{select="select1",text="Select",visible=true,onToggled="mySelect",value='2',options={{type='option',text='Option 1',value='1'},{type='option',text='Option 2',value='2'},{type='option',text='Option 3',value='3'}}}
--%%u:{multi="multi1",text="Multi",visible=true,values={"1","3"},onToggled="myMulti",options={{type='option',text='Option 1',value='1'},{type='option',text='Option 2',value='2'},{type='option',text='Option 3',value='3'}}}


function QuickApp:testBtn1(ev)
  print("testBtn1")
end

function QuickApp:testBtn2(ev)
  print("testBtn2")
end

function QuickApp:testBtn3()
  print("testBtn3")
end

function QuickApp:testBtn5(ev)
  print("testBtn5")
end

function QuickApp:mySwitch(ev)
  print("mySwitch",ev.values[1])
end

function QuickApp:mySlider(ev)
  print("mySlider",ev.values[1])
end

function QuickApp:mySelect(ev)
  print("mySelect",ev.values[1])
end

function QuickApp:myMulti(ev)
  print("myMulti",json.encode(ev.values[1]))
end

function QuickApp:onInit()
  self:debug("onInit")
  setInterval(function() print("PING") end,2000) -- keep script alive
end
