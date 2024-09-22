#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
#use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI::Session;
use CGI qw(:cgi);
use Digest::MD5 qw(md5_hex);
use Build_Menu qw(:DEFAULT $idd);

my $SID;
my $method;

if (defined(cookie('SID'))) {
        $SID=cookie('SID');
        $SID=~s/\0//g; $SID=~s/\.\.//g; $SID=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        $method='cookies';
        }
elsif (defined(param('SID'))) {
        $SID=param('SID');
        $SID=~s/\0//g; $SID=~s/\.\.//g; $SID=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        $method='path';
        }
else {
        print "Location: http://localhost:6080\n\n";
        exit();
        }

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:spending",User=>"root", Password=>""}) or die CGI::Session->errstr();
$sess->name('SID');

#Если сессия пустая
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#Если вермя сессии истекло
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#Если IP не совпадают
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#Присваиваем переменным логин и пароль пользователя из сессии
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $CALENDAR_SEKRETARIAT=$sess->param('CALENDAR_SEKRETARIAT');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

    if ($CALENDAR_SEKRETARIAT==1) #Смотрим имеет ли доступ пользователь к модулю "Календарь".
    {
        #Подгружаем название организации для вывода ее на странице
        open FF, "<txt_data/name_org.txt";
        my @name_org=<FF>;
        foreach my $str (@name_org)
        {
           $str=~s/\0//g;
           $str=~s/\.\.//g;
           $str=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        }
        close (FF) or die $!;
        #########################################

        print "Content-type: text/html\n\n";
        print <<HTML;
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset='windows-1251'>
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>@name_org</title>
        <link rel="stylesheet" type="text/css" href="../CSS/easyui.css">
        <link rel="stylesheet" type="text/css" href="../CSS/icon.css">
        <link rel="stylesheet" type="text/css" href="../CSS/demo.css">
        <link rel="stylesheet" type="text/css" href="../CSS/dhtmlxscheduler.css">
        <link rel="stylesheet" href="../CSS/styles.css">
        <link rel="stylesheet" href="../CSS/multiline_scheduler.css">
		<link rel="stylesheet" href="../CSS/scheduler_color_events.css">
        <script type="text/javascript" src="../JS/jquery.min.js"></script>
        <script type="text/javascript" src="../JS/jquery.easyui.min.js"></script>
        <script type="text/javascript" src="../JS/dhtmlxscheduler.js"></script>
        <script type="text/javascript" src="../JS/dhtmlxscheduler_year_view.js"></script>
        <script type="text/javascript" src="../JS/dhtmlxscheduler_agenda_view.js"></script>        
        <script type="text/javascript" src="../JS/locale_ru.js" charset="utf-8"></script>
        <script type="text/javascript" src="../JS/dhtmlxscheduler_quick_info.js"></script>        
        <script type="text/javascript" src="../JS/dhtmlxscheduler_active_links.js"></script>
		<script type="text/javascript" src="../JS/dhtmlxscheduler_key_nav.js"></script> 
		<script type="text/javascript" src="../JS/dhtmlxscheduler_limit.js"></script> 
		<script type="text/javascript" src="../JS/dhtmlxscheduler_editors.js"></script> 
        <script src="../JS/script.js"></script>

        <script>
        function confirm1(){
        \$.messager.confirm('Внимание', 'Вы уверены, что необходимо выйти', function(r){
        if (r){
        //alert('confirmed: '+r);
        window.location.replace("/cgi-bin/exit.cgi?SID=$SID");
        }     });  }   </script>

        <!--Increae time of life session-->
        <script>
        \$(document).mouseup(function (e){
        \$.ajax({
                url: '/cgi-bin/session_alive.cgi?SID=$SID',
                success: function(){
                window.location.replace("http://localhost:6080")}
                                });  });    </script>

        <script> //Отправка формы смены пароля
        function call() {
        var msg   = \$('#ff').serialize();
        \$.ajax({
          type: 'GET',
          url: 'change_psw.cgi?SID=$SID',
          data: msg,
          success: function(res) {alert(res.result); \$('#ff')[0].reset(); \$('#w').window('close');},
          error: function() {alert("did not work");}
        });

       }
       </script>
       
       <script type="text/javascript"> //Инициируем календарь
	function init() {
		scheduler.config.xml_date="%Y-%m-%d %H:%i";
		scheduler.config.prevent_cache = true;
		scheduler.config.details_on_create = true;
		scheduler.config.details_on_dblclick = true;
		scheduler.config.show_loading = true;
        scheduler.config.separate_short_events = true;
        scheduler.config.touch = "force";
		scheduler.config.full_day = true;
		scheduler.config.mark_now = true;
		scheduler.config.max_month_events = 5;
		scheduler.config.resize_month_events = true;
		
		scheduler.templates.event_class=function(start, end, event){
				var css = "";

				if(event.subject) // if event has subject property then special class should be assigned
					css += "event_"+event.subject;

				if(event.id == scheduler.getState().select_id){
					css += " selected";
				}
				return css; // default return
				
			    };

		var subject = [
				{ key: '', label: '' },
				{ key: 'linguaterria', label: 'Лингватеррия' },
				{ key: 'test', label: 'Тестирование' },
				{ key: 'event', label: 'Событие' },
				{ key: 'dogovor', label: 'Договор (Заключение/Перезаключение)' },
				{ key: 'calls', label: 'Звонки' }
		        ];
				
		scheduler.config.lightbox.sections = [
				{name:"Описание события", height:130, map_to:"text", type:"textarea" , focus:true},
				{name:"Подробности", height:43, type:"textarea", map_to:"details" },
				{name:"time", height:72, type:"time", map_to:"auto"},
				{name:"Напомнить!", map_to:"single_checkbox", type:"checkbox", checked_value: "1", unchecked_value: "0"},
				{name:"Тип события", height:20, type:"select", options: subject, map_to:"subject"}
			];
				
		scheduler.init('scheduler_here',new Date(),"week");
                                     scheduler.setLoadMode("week");
		scheduler.load("get_calendar_events.cgi?SID=$SID","json");
		
		
		//Смотрим чтобы сообщение не было пустым или слишком коротким
		scheduler.attachEvent("onEventSave",function(id,ev){
		     if (!ev.text) {
		     dhtmlx.alert("Событие не может быть пустым!");				
		     return false;
		     }
		     if (ev.text.length<10) {
		     dhtmlx.alert("Текст слишком короткий!");				
		     return false;
		     }
		return true;
		});
				
		//Добавляем событие в календарь
		scheduler.attachEvent("onEventAdded",function(id){
		    var ev = scheduler.getEvent(id);
		    var format = scheduler.templates.xml_format;
		    var path="save_calendar_events.cgi?SID=$SID"+"&start_date="+format(ev.start_date)+"&end_date="+format(ev.end_date)+"&text="+ev.text+"&details="+ev.details+"&subject="+ev.subject+"&single_checkbox="+ev.single_checkbox;
                    dhtmlxAjax.get(path);                   
                });
                
                //Редактируем выбранное событие в календаре
                scheduler.attachEvent("onEventChanged",function(id){
		    var ev = scheduler.getEvent(id);
		    var format = scheduler.templates.xml_format;
		    var path="update_calendar_events.cgi?SID=$SID"+"&start_date="+format(ev.start_date)+"&end_date="+format(ev.end_date)+"&text="+ev.text+"&details="+ev.details+"&id="+ev.id+"&subject="+ev.subject+"&single_checkbox="+ev.single_checkbox;
                    dhtmlxAjax.get(path);                                       
                });
                
                 //Удаляем выбранное событие в календаре
                scheduler.attachEvent("onEventDeleted",function(id){
		    var ev = scheduler.getEvent(id);
		    var format = scheduler.templates.xml_format;
		    var path="delete_calendar_events.cgi?SID=$SID"+"&id="+id;
                    dhtmlxAjax.get(path);                                                                                                 
                });

                
                scheduler.templates.event_bar_date = function(start,end,ev){
                return "• <b>"+scheduler.templates.event_date(start)+" - "+scheduler.templates.event_date(end)+"</b> ";
                };
		
	}
        </script>


        </head>
        <body class="easyui-layout" onload="init();">
        <!--Верхний DIV - заголовок -->
        <div data-options="region:'north',border:false" style="height:100px;background:#f0993c;padding:10px;"><h1 class="shd">@name_org</h1>
        <!--DIV В котором лежат кнопки панели-->
HTML
        
        #Подгружаем кнопки, которые лежат на верхней панеле
        open FF1, "<txt_data/buttons_panel.txt";
        my @buttons_panel=<FF1>;
        foreach my $str_but (@buttons_panel)
        {
           $str_but=~s/\0//g;
           $str_but=~s/\.\.//g;
           $str_but=~s/[<]*script[^>]*>.*[<]*\/script[>]*//i; #На всяк случай удаляем тэги <script>
		   $str_but=~s/SID=\$SID/SID=$SID/i; #Подставляем регуляркой ссам SID в тексте вместо переменной $SID. Сам он не подставляется, т.к. кнопки грузятся из текстового файла.
        }
        close (FF1) or die $!;        
        print @buttons_panel;
        #########################################

        print <<HTML1;
        <!--Конец DIV В котором лежат кнопки панели-->
        </div>
        <!--Конец верхний DIV - Заголовок -->

        <!--Левый DIV раздел меню -->
        <div data-options="region:'west',split:false,title:'Меню'" style="width:205px;">

        <div id='cssmenu'>
        <ul>
HTML1
        #Подгружаем и вставляем меню
        my $us_id=$sess->param('USER_ID'); #Читаем из сессии USER_ID
        Build_Menu->menu($us_id, $SID); #В параметр функции вставляем ID пользователя для вывода меню
        
        print <<HTML_e;
        </ul>
        </div>

        </div>
        <!--КОнец Левый DIV раздел меню -->

        <!-- Правый DIV раздел подробности -->
        <!-- <div data-options="region:'east',split:true,title:'Подробности'" style="width:30%;padding:1px;">  -->
        <!-- </div> -->
        <!-- Конец Правый DIV раздел подробности -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->

        <!-- Центральный DIV -рабочая область -->
        <div data-options="region:'center',title:'Рабочая область - Календарь. Пользователь: $formLogin'">
        
           <!-- Календарь -->
           <div id="scheduler_here" class="dhx_cal_container" style='width:100%; height:100%;'>
                <div class="dhx_cal_navline">
                  <div class="dhx_cal_prev_button">&nbsp;</div>
                  <div class="dhx_cal_next_button">&nbsp;</div>
                  <div class="dhx_cal_today_button"></div>
                  <div class="dhx_cal_date"></div>
                  <div class="dhx_cal_tab" name="day_tab" style="right:204px;"></div>
                  <div class="dhx_cal_tab" name="week_tab" style="right:140px;"></div>
                  <div class="dhx_cal_tab" name="month_tab" style="right:76px;"></div>
                  <div class="dhx_cal_tab" name="year_tab" style="right:268px;"></div>
                  <div class="dhx_cal_tab" name="agenda_tab" style="right:280px;"></div>
               </div>
               <div class="dhx_cal_header"></div>
               <div class="dhx_cal_data"></div>       
           </div>        
           <!-- Конец Календарь -->
           
        </div>
        <!-- Конец центральный DIV -рабочая область -->

        <!-- Форма изменения пароля -->
        <div id="w" class="easyui-window" title="Смена пароля" data-options="modal:true,closed:true,iconCls:'icon-save'" style="width:370px;height:170px;padding:10px;">
        <form id="ff" action="javascript:void(null);" onsubmit="call()" method="post" enctype="multipart/form-data">
            <table>
                <tr>
                    <td>Текущий пароль:</td>
                    <td><input id="curr_psw" name="curr_psw" type="password" class="f1 easyui-textbox"></input></td>
                </tr>
                <tr>
                    <td>Новый пароль:</td>
                    <td><input name="new_psw" type="password" class="f1 easyui-textbox"></input></td>
                </tr>
                <tr>
                    <td>Еще раз:</td>
                    <td><input name="new_psw1" type="password" class="f1 easyui-textbox"></input></td>
                </tr>
                <tr>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                </tr>
                <tr>
                    <td></td>
                    <td><input type="submit" value="Подтвердить"></input></td>
                </tr>
            </table>
        </form>
    </div>
    <!-- Конец форма изменения пароля -->
        </body>
        </html>
HTML_e

        #Продлеваем время жизни сессии
        $sess->atime(time());
        $sess->flush();
  }
  else
  {
       &f_delete_session(); #Удаляем сессию
       
       print "Content-type: text/html\n\n";
       print <<HTML3;
       
       <!doctype html>
       <html>
       <head>
       <meta charset="windows-1251">
       <title>Нет доступа</title>

       <script type="text/javascript">
       setTimeout('location.replace("http://localhost:6080")', 3000);
       </script>

       <noscript>
       <meta http-equiv="refresh" content="3; url=http://localhost:6080">
       </noscript>

       <style type="text/css">
       body {
	       background-color: #4E5869;
       }
       .zagolovok {
	            font-family: "Times New Roman", Times, serif;
	            color: #FF0;	
       }
       </style>
       </head>

       <body>
       <h1 align="center" class="zagolovok"><strong>У вас нет доступа к данному модулю!</strong></h1>
       </body>
       </html>       
HTML3
   }   

#Удаление сессии
sub f_delete_session {
         #Удаляем куки
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://localhost:6080');
         print "Set-Cookie: $cookies\n";
         #Удаляем сессию
         $sess->delete();
         $sess->flush();
        }

#Добавление SID к URL-адресу
sub f_add_sid {
        my $url=shift();
        if ($method eq 'path') {
                if (defined($SID) && $url !=~ m/SID=/) {
                        if ($url !=~ m/\?/) {
                                $url.="?SID=".$SID;
                                }
                        else {
                                $url.="&SID=".$SID;
                             }
                        }
                }
                return $url;
              }

}
else { print "Location: http://localhost:6080\n\n"; }