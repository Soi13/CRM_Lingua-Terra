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
my $RESERV_SEKRETARIAT=$sess->param('RESERV_SEKRETARIAT');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

     if ($RESERV_SEKRETARIAT==1) #Смотрим имеет ли доступ пользователь к модулю "Резерв".
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
        <script type="text/javascript" src="../JS/jquery.min.js"></script>
        <script type="text/javascript" src="../JS/jquery.easyui.min.js"></script>
        <script type="text/javascript" src="../JS/dhtmlxscheduler.js"></script>
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

       <script>
       function doSearch(){
       \$('#dg').datagrid('load',{
       //fio: \$('#fio').val()
	   fio: \$('#fio').textbox('getText')
       });
       }
       </script>

       <script>
       \$(function(){
       \$('#dg').datagrid({
       onSelect:function(index){
       var row = \$('#dg').datagrid('getSelected');
       //Загружаем и заполняем подробности по заявкам
       \$('#pg').propertygrid({
       method:'get',
       url: 'get_zayavki_reserv_detail.cgi?id_z='+row.ID+'&SID=$SID',
       showGroup: true,
       showHeader: false,
       scrollbarSize: 0
       });
       //////////////////////////////////////////
                                }
                        });
                });
        </script>
                
    
     <script type="text/javascript">
        function myformatter(date){
            var y = date.getFullYear();
            var m = date.getMonth()+1;
            var d = date.getDate();
            return y+'-'+(m<10?('0'+m):m)+'-'+(d<10?('0'+d):d);
        }
        function myparser(s){
            if (!s) return new Date();
            var ss = (s.split('-'));
            var y = parseInt(ss[0],10);
            var m = parseInt(ss[1],10);
            var d = parseInt(ss[2],10);
            if (!isNaN(y) && !isNaN(m) && !isNaN(d)){
                return new Date(y,m-1,d);
            } else {
                return new Date();
            }
        }
    </script>
   
       
        <script>//Включение Keyboard Navigation
        \$(function(){
        \$('#dg').datagrid('getPanel').panel('panel').attr('tabindex',0).bind('keydown',function(e){
	switch(e.keyCode){
		case 38:	// up
			var selected = \$('#dg').datagrid('getSelected');
			if (selected){
				var index = \$('#dg').datagrid('getRowIndex', selected);
				\$('#dg').datagrid('selectRow', index-1);
			} else {
				\$('#dg').datagrid('selectRow', 0);
			}
			break;
		case 40:	// down
			var selected = \$('#dg').datagrid('getSelected');
			if (selected){
				var index = \$('#dg').datagrid('getRowIndex', selected);
				\$('#dg').datagrid('selectRow', index+1);
			} else {
				\$('#dg').datagrid('selectRow', 0);
			}
			break;
	}
       });
       });
       </script>
       
             
       <script>//Установка фильтра
       function doFilter(){
       
       //Проверка, выбран хотя бы один параметр фильтрации
       if((!\$("#radio_WHO_GET_ZAYAV").prop("checked")) && (!\$("#radio_SOURCE_ZAYAV").prop("checked")) && (!\$("#radio_DATE_OF_ZAYAV_FROM").prop("checked")) && (!\$("#radio_AGE_STUDENT").prop("checked")) && (!\$("#radio_BRANCH").prop("checked")) && (!\$("#radio_LANGUAGE").prop("checked")) && (!\$("#radio_LEVEL_KNOWLEDGE").prop("checked")) && (!\$("#radio_DATE_OF_TEST_FROM").prop("checked")) && (!\$("#radio_erase_filter").prop("checked")) && (!\$("#radio_DATE_OF_BORN_FROM").prop("checked"))) {
	    \$.messager.alert('Внимание','Не выбран параметр фильтрации!','warning');
	    return;
        }        
               
       ///////////////////
       if(\$("#radio_WHO_GET_ZAYAV").prop("checked")) { 
              \$('#dg').datagrid('load',{
             who_get_zayav: \$('#WHO_GET_ZAYAV').combobox('getValue')                                          
              });
              \$('#lb').text('Установлен фильтр по "Кто получил заявку"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_SOURCE_ZAYAV").prop("checked")) { 
              \$('#dg').datagrid('load',{
             source_zayav: \$('#SOURCE_ZAYAV').combobox('getValue')
              });
              \$('#lb').text('Установлен фильтр по "Источник заявки"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_DATE_OF_ZAYAV_FROM").prop("checked")) { 
              \$('#dg').datagrid('load',{
             date_of_zayav_from: \$('#DATE_OF_ZAYAV_FROM').datebox('getValue'),
             date_of_zayav_to: \$('#DATE_OF_ZAYAV_TO').datebox('getValue')             
              });
              \$('#lb').text('Установлен фильтр по "Дата заявки"');
       }
       ///////////////////
              
       ///////////////////
       if(\$("#radio_AGE_STUDENT").prop("checked")) { 
              \$('#dg').datagrid('load',{
             age: \$('#AGE_STUDENT').val()
              });
              \$('#lb').text('Установлен фильтр по "Возраст студента"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_DATE_OF_BORN_FROM").prop("checked")) { 
              \$('#dg').datagrid('load',{
             date_of_born_from: \$('#DATE_OF_BORN_FROM').datebox('getValue'),
             date_of_born_to: \$('#DATE_OF_BORN_TO').datebox('getValue')             
              });
              \$('#lb').text('Установлен фильтр по "Дата рождения"');
       }
       ///////////////////
              
       ///////////////////
       if(\$("#radio_BRANCH").prop("checked")) { 
              \$('#dg').datagrid('load',{
             branch: \$('#BRANCH').combobox('getValue')
              });
              \$('#lb').text('Установлен фильтр по "Филиал"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_LANGUAGE").prop("checked")) { 
              \$('#dg').datagrid('load',{
             language: \$('#LANGUAGE').combobox('getValue')
              });
              \$('#lb').text('Установлен фильтр по "Язык"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_LEVEL_KNOWLEDGE").prop("checked")) { 
              \$('#dg').datagrid('load',{
             level_knowledge: \$('#LEVEL_KNOWLEDGE').combobox('getValue')
              });
              \$('#lb').text('Установлен фильтр по "Уровень владения"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_DATE_OF_TEST_FROM").prop("checked")) { 
              \$('#dg').datagrid('load',{
             date_of_test_from: \$('#DATE_OF_TEST_FROM').datebox('getValue'),
             date_of_test_to: \$('#DATE_OF_TEST_TO').datebox('getValue')             
              });
              \$('#lb').text('Установлен фильтр по "Дата теста"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_erase_filter").prop("checked")) { 
              \$('#dg').datagrid('load',{
             erase_filter: 'switch_filter'
              });
              \$('#lb').text('');
       }
       ///////////////////
 
       \$('#fm_filter').form('clear'); \$('#dlg_filter').dialog('close'); //Закрываем и форму фильтрации и очищаем поля
 
       }
       </script>//Конец скрипта установки фильтра
       
                      
       <script> //Возможность поиска по нажатию Enter
       \$(document).ready(function(){
	var t = \$('#fio');
	t.textbox('textbox').bind('keydown', function(e){
	   if (e.keyCode == 13) 
	   { 
	      doSearch();
	   }
	});	
        })
        </script>
        
	    <script> 
        \$(function(){
        //Добавление полю TextBox события KeyUp для поиска на лету
        \$('#fio').textbox({
	                      inputEvents:\$.extend({},\$.fn.textbox.defaults.inputEvents,{
		              keyup:function(e){
			                          doSearch();
		                               }
	                      })
                           })
        
        })
        </script>
    
        </head>
 
 
        <body class="easyui-layout">
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
        <div data-options="region:'east',split:true,title:'Подробности'" style="width:30%;padding:1px;">
        
         <table id="pg" style="width:100%"></table>
        
        </div>
        <!-- Конец Правый DIV раздел подробности -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->

        <!-- Центральный DIV -рабочая область -->
        <div data-options="region:'center',title:'Рабочая область - Резерв. Пользователь: $formLogin'">

        <table id="dg" title="Резерв" class="easyui-datagrid" style="width:100%;height:100%"
        method="get"
        url="get_zayavki_reserv.cgi?SID=$SID"
        toolbar="#tb, #toolbar"
        rownumbers="true" fitColumns="true" singleSelect="true" pagination="true" sortName="FIO_STUDENT" sortOrder="asc">

        <thead>
        <tr>
            <th field="ID" width="15" sortable="true" hidden="true">ID1</th>
            <th field="DATE_GET_ZAYAV" width="20" sortable="true">Дата заявки</th>
            <th field="FIO_STUDENT" width="60" sortable="true">ФИО студента</th>
            <th field="LANG" width="60" sortable="true">Курс</th>
            <th field="LEVEL" width="25" sortable="true">Уровень владения</th>            
            <th field="AGE_STUDENT" width="25">Возраст студента</th>
            <th field="BR" width="27">Филиал</th>
        </tr>
        </thead>
        </table>
        <div id="toolbar">
        <a href="#" class="easyui-linkbutton" iconCls="icon-filter" plain="true" onclick="\$('#dlg_filter').window('open').dialog('center').dialog('setTitle','Фильтр')">Фильтр</a>
        <span id="lb" style="float:right; color: #F00; font-weight: bold;"></span>
        </div>

        <!-- Панель посика -->
        <div id="tb" style="padding:3px">
             <span>Поиск по ФИО студента:</span>
             <input id="fio" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
             <a href="#" class="easyui-linkbutton" plain="false" onclick="doSearch()" style="border-radius:5px; width:100px;">Искать</a>
        </div>
        <!-- Конец Панель для поиска -->

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
    
     
    <!-- Форма установки фильтра заявки -->    
    <div id="dlg_filter" class="easyui-dialog" style="width:530px;height:400px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Установка фильтра</div>
        <form id="fm_filter" novalidate>
            <table>
                <tr>
                    <td><label><input id="radio_WHO_GET_ZAYAV" name="radio" type="radio" value="0" />Заявку принял:</label></td>
                    <td><input id="WHO_GET_ZAYAV" name="WHO_GET_ZAYAV" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'users_get_zayav.cgi?SID=$SID', method: 'get'"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_SOURCE_ZAYAV" name="radio" type="radio" value="1" />Источник заявки:</label></td>
                    <td><input id="SOURCE_ZAYAV" name="SOURCE_ZAYAV" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', valueText: 'text', url: 'users_get_source_zayav.cgi?SID=$SID', method: 'get'"></input></td>
                </tr>
                <tr>
                    <td><label><input id="radio_DATE_OF_ZAYAV_FROM" name="radio" type="radio" value="2" />Дата заявки:    От--</label></td>
                    <td><input id="DATE_OF_ZAYAV_FROM" name="DATE_OF_ZAYAV_FROM" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser">   До--<input id="DATE_OF_ZAYAV_TO" name="DATE_OF_ZAYAV_TO" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_AGE_STUDENT" name="radio" type="radio" value="3" />Возраст студента:</label></td>
                    <td><input id="AGE_STUDENT" name="AGE_STUDENT" class="easyui-textbox"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_DATE_OF_BORN_FROM" name="radio" type="radio" value="9" />Дата рожд.:    От--</label></td>
                    <td><input id="DATE_OF_BORN_FROM" name="DATE_OF_BORN_FROM" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser">   До--<input id="DATE_OF_BORN_TO" name="DATE_OF_BORN_TO" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_BRANCH" name="radio" type="radio" value="4" />Филиал:</label></td>
                    <td><input id="BRANCH" name="BRANCH" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', valueText: 'text', url: 'get_branches.cgi?SID=$SID', method: 'get'"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_LANGUAGE" name="radio" type="radio" value="5" />Курс:</label></td>
                    <td><input id="LANGUAGE" name="LANGUAGE" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', valueText: 'text', url: 'get_languages.cgi?SID=$SID', method: 'get'"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_LEVEL_KNOWLEDGE" name="radio" type="radio" value="6" />Уровень владения:</label></td>
                    <td><input id="LEVEL_KNOWLEDGE" name="LEVEL_KNOWLEDGE" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', valueText: 'text', url: 'get_level_knowledge.cgi?SID=$SID', method: 'get'"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_DATE_OF_TEST_FROM" name="radio" type="radio" value="7" />Дата тестирования:  От--</label></td>
                    <td><input id="DATE_OF_TEST_FROM" name="DATE_OF_TEST_FROM" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser">   До--<input id="DATE_OF_TEST_TO" name="DATE_OF_TEST_TO" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser"></td>
                </tr>                
                <tr>
                    <td><label><input id="radio_erase_filter" name="radio" type="radio" value="8" /><strong>Снять фильтры:</strong></label></td>                    
                </tr>
            </table>    
        </form>
    </div>
    <div id="dlg-buttons">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="doFilter()" style="width:100px">Установить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_filter').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма установки фильтра заявки -->
    
    
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