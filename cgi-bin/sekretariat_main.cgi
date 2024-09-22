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
my $days_expired=$sess->param('days_expired_passw');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {
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

        my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time); 
        $mon=$mon+1;
        $year=$year+1900;

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
        <link rel="stylesheet" href="../CSS/styles.css">
        <link rel="stylesheet" type="text/css" href="../CSS/dhtmlxchart.css">
        <link rel="stylesheet" type="text/css" href="../CSS/font_roboto/roboto.css">
		<link rel="stylesheet" href="../amcharts/plugins/export/export.css" type="text/css" media="all" />  
        <script type="text/javascript" src="../JS/jquery.min.js"></script>
        <script type="text/javascript" src="../JS/jquery.easyui.min.js"></script>
        <script src="../JS/script.js"></script>
        <script src="../JS/dhtmlxchart.js"></script>
		<script src="../amcharts/amcharts.js"></script>
        <script src="../amcharts/funnel.js"></script>
        <script src="../amcharts/plugins/export/export.min.js"></script>
        <script src="../amcharts/plugins/dataloader/dataloader.min.js" type="text/javascript"></script>
        <script src="../amcharts/themes/light.js"></script>

        <script>
        var chart = AmCharts.makeChart( "chartdiv", {
        "type": "funnel",
        "theme": "light",
        "dataLoader": {
                        "url": "get_sales_funnel.cgi?SID=$SID",
                        "format": "json"
                      },
        "balloon": {
                 "      fixedPosition": true
                   },
        "valueField": "value",
        "titleField": "title",
        "marginRight": 240,
        "marginLeft": 50,
        "startX": -500,
        "depth3D": 0,
        "angle": 40,
        "outlineAlpha": 1,
        "outlineColor": "#FFFFFF",
        "outlineThickness": 2,
        "labelPosition": "right", 
        "marginTop": 40,  
        "allLabels": [
		      {
			"text": "Воронка продаж за текущий месяц ($mon.$year)",
			"bold": true,
			"x": 70,
			"y": 25
		      }
                     ],  
        "balloonText": "[[title]]: [[value]] шт.[[description]]",
        "export": {
                     "enabled": false
                  }
        });
        </script>

		
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
       
       <script>
		var myPieChart;	
                                     var myPieChart_age;	
		function doOnLoad() {
		        		        
			myPieChart = new dhtmlXChart({
				view:"pie3D",
				container:"chartbox",
				value:"#count#",
				
				tooltip:"Кол-во: <b>#count#</b>",
				legend:{
					width: 75,
					align:"right",
					valign:"middle",
					template:"#sex#"
				},
				gradient:1,
				shadow:true,
				
				color:function(obj){
                               if (obj.sex == 'Ж') return "#ff9900";
                               if (obj.sex == 'М') return "#66cc00";
                               }
			});
			myPieChart.load("get_sex.cgi?SID=$SID", "json");

            //Вывод диаграммы по филиалам
			myPieChart_age = new dhtmlXChart({
				view:"pie3D",
				container:"chartbox_branch",
				value:"#count#",
				tooltip:"Кол-во студентов: <b>#count#</b>",
				legend:{
					width: 200,
					align:"right",
					valign:"middle",
					template:"#BRANCH#"
				},
				gradient:1,
				shadow:true
			});
			myPieChart_age.load("get_branch.cgi?SID=$SID", "json");


            
			//Вывод диаграммы по дате создания/заполнения студента
			myLineChart_date_reg = new dhtmlXChart({
				view:"spline",
				container:"chartbox_date_reg",
				value:"#count#",
				tooltip:"Кол-во регистраций студентов: <b>#count#</b>",
				gradient:1,
				shadow:true,
				xAxis:{
                                       title:"Дата/Число регистрации студента",
                                       template:"#day#"
                                      },
                                yAxis:{
                                       title:"Кол-во регистраций"                                       
                                      },
        
			});
			myLineChart_date_reg.load("get_count_reg_students.cgi?SID=$SID", "json");
            
			
            
			//Вывод диаграммы по дате создания заявки
			myLineChart_date_zayav = new dhtmlXChart({
				view:"spline",
				container:"chartbox_date_zayav",
				value:"#count#",
				tooltip:"Кол-во принятых заявок: <b>#count#</b>",
				gradient:1,
				shadow:true,
				xAxis:{
                                       title:"Дата/Число принятой заявки",
                                       template:"#day#"
                                      },
                                yAxis:{
                                       title:"Кол-во регистраций заявок"                                                                        
                                      },
        
			});
			myLineChart_date_zayav.load("get_count_reg_zayav.cgi?SID=$SID", "json");
			
			
			//Выводим ожидаемый процент оплаты в текущем месяце и процент реально оплативших
			myPieChart_debt = new dhtmlXChart({
				view:"pie3D",
				container:"chartbox_debt",
				value:"#summ#",
				
				tooltip:"<b>#summ# %</b>",
				legend:{
					width: 200,					
					align:"right",
					valign:"middle",
					template:"#PAY#"
				},
				gradient:1,
				shadow:true,
				
				color:function(obj){
                               if (obj.PAY == 'Не оплачено, %') return "#f36ee2";
                               if (obj.PAY == 'Оплачено, %') return "#54d2f2";
                               }
			});
			myPieChart_debt.load("get_debts_pays.cgi?SID=$SID", "json");


		}
	</script>

                   <script>
	\$(function(){
	\$('#panel_birthday').panel({
                                      width:352,
                                      height:252,
                                      href:'get_birthdays.cgi?SID=$SID'  
    
                                   }); 
	            });
	</script>
	
	<script> //Загружаем повестку дня для пользователя
    \$(function(){	
       \$.ajax({
            type: 'GET',
            url: 'get_agenda.cgi?SID=$SID',
            cache: false,
            success: function(res1) {   
                                       if (res1.rows.length>0)
                                       {
                                        //alert(res1.rows[0].START_DATE);
                                        \$('#dlg_open_agenda').window('open').dialog('center').dialog('setTitle','Повестка дня из личного календаря');
                                        \$('#dg_agenda').datagrid({data: res1});                                     
                                       }
                                     },
            error: function() {alert("did not work");}
            });
                
       })
    </script>   
	
	<script>//Функция выделения цветом события
    \$(function(){       
       \$('#dg_agenda').datagrid({
	      rowStyler: function(index,row){
		         if (row.KIND_EVENT=="calls"){ return 'background-color:blue;color:#fff;'; }
		         if (row.KIND_EVENT=="linguaterria"){ return 'background-color:#FC5BD5;color:#fff;'; }
		         if (row.KIND_EVENT=="dogovor"){ return 'background-color:red;color:#fff;'; }
		         if (row.KIND_EVENT=="test"){ return 'background-color:orange;color:#fff;'; }
		         if (row.KIND_EVENT=="event"){ return 'background-color:#36BD14;color:#fff;'; }
		         if (row.KIND_EVENT==""){ return 'background-color:#1796b0;color:#fff;'; }
	            }  
            });         
    })
    </script>
	
	 <script>
       \$(function(){  
           var days=$days_expired;
           
           switch (days){
             case 1:
             \$.messager.alert('Информация', 'Срок действия пароля истекает через 1 день. Рекомендуется изменить его, иначе учетная запись будет заблокирована!', 'info');
             break;
             case 2:
             \$.messager.alert('Информация', 'Срок действия пароля истекает через 2 дня. Рекомендуется изменить его, иначе учетная запись будет заблокирована!', 'info');
             break;
             case 3:
             \$.messager.alert('Информация', 'Срок действия пароля истекает через 3 дня. Рекомендуется изменить его, иначе учетная запись будет заблокирована!', 'info');
             break;
             case 4:
             \$.messager.alert('Информация', 'Срок действия пароля истекает через 4 дня. Рекомендуется изменить его, иначе учетная запись будет заблокирована!', 'info');
             break;
             case 5:
             \$.messager.alert('Информация', 'Срок действия пароля истекает через 5 дней. Рекомендуется изменить его, иначе учетная запись будет заблокирована!', 'info');
             break;               
           }      
        })
     </script>
    

        </head>
        <body class="easyui-layout" onload="doOnLoad();">
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
        <!-- <div data-options="region:'east',split:true,title:'Подробности'" style="width:30%;padding:1px;"> -->
        <!-- </div> -->
        <!-- Конец Правый DIV раздел подробности -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->

        <!-- Центральный DIV -рабочая область -->
        <div data-options="region:'center',title:'Рабочая область - Главная. Пользователь: $formLogin'">
        
     <!-- Диаграмма и ДР студентов -->
        <div style="float:left">
          <div id="chartbox" style="width:350px;height:300px;border:1px solid #c0c0c0;">Статистика по половому признаку</div>
          <div id="panel_birthday" style="border-color:#999; padding-top:10px;"><header style="background-color: #FFFFFF; border-color:#999; color:red;">Сегодня день рождения у:</header></div>
        </div>
        <div style="float:left">
          <div id="chartbox_branch" style="width:500px;height:300px;border:1px solid #c0c0c0;">Статистика по филиалам</div>
          <div id="chartbox_date_reg" style="width:500px;height:250px;border:1px solid #c0c0c0;">Кол-во регистраций студентов в текущем месяце ( $mon.$year)</div> 
        </div>
        <div style="float:left">
          <div id="chartbox_date_zayav" style="width:500px;height:300px;border:1px solid #c0c0c0;">Кол-во принятых заявок в текущем месяце ( $mon.$year)</div>
		  <div id="chartbox_debt" style="width:500px;height:250px;border:1px solid #c0c0c0;">Ожидаемый процент оплат в текущем месяце и процент оплаченных сумм</div>
        </div>
		<div>
          <div id="chartdiv" style="width:650px; height:250px; font-size:11px;"></div>
        </div>
        <!-- Конец Диаграмма и ДР студентов-->              

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
	
	<!-- Форма вывода повестки дня -->    
    <div id="dlg_open_agenda" class="easyui-dialog" style="width:80%;height:500px;padding:10px 5px 0px 5px;"
            closed="true" modal="true" buttons="#dlg_buttons_agenda" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">             
        <h1 class="shad">Повестка дня</h1>                   
        <table id="dg_agenda" class="easyui-datagrid" style="width:100%;height:75%"
        method="get" rownumbers="true" singleSelect="true" fitColumns="true" sortOrder="asc" striped=true>
        <thead>
        <tr>
            <th field="ID" width="10" hidden="true">ID</th>
            <th field="START_DATE" width="30">Дата и время начала события</th>
            <th field="TEXT_MESSAGE" width="70">Событие</th>
            <th field="DETAILS" width="60">Подробности</th>                                    
            <th field="KIND_EVENT" width="10" hidden="true">ID</th>
        </tr>
        </thead>
        </table>                
    </div> 
    <div id="dlg_buttons_agenda">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="javascript:\$('#dlg_open_agenda').dialog('close')" style="width:90px">Закрыть</a>
    </div>
    <!-- Конец Форма вывода повестки дня -->
	
        </body>
        </html>
HTML_e

#Продлеваем время жизни сессии
$sess->atime(time());
$sess->flush();

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