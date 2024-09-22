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
my $TEACHERS_SEKRETARIAT=$sess->param('TEACHERS_SEKRETARIAT');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

    if ($TEACHERS_SEKRETARIAT==1) #Смотрим имеет ли доступ пользователь к модулю "Учителя".
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
        <script type="text/javascript" src="../JS/jquery.min.js"></script>
        <script type="text/javascript" src="../JS/jquery.easyui.min.js"></script>
        <script type="text/javascript" src="../JS/dhtmlxscheduler.js"></script>
        <script type="text/javascript" src="../JS/locale_ru.js" charset="utf-8"></script>     
        <script type="text/javascript" src="../JS/dhtmlxscheduler_readonly.js"></script>
        <script type="text/javascript" src="../JS/dhtmlxscheduler_quick_info.js"></script>
        <script type="text/javascript" src="../JS/dhtmlxscheduler_active_links.js"></script> 
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
       //Загружаем и заполняем подробности по преподу
       \$('#pg').propertygrid({
       method:'get',
       url: 'get_teachers_detail.cgi?num='+row.ID+'&SID=$SID',
       showGroup: true,
       showHeader: false,
       scrollbarSize: 0
       });
       //////////////////////////////////////////
            
       
       //Обновление календаря при перемещении по преподам. Загрузка записей выделенного студента
	scheduler.clearAll();
	scheduler.load("get_calendar_4_teachers.cgi?SID=$SID"+"&num_tec="+row.ID,"json");		
	scheduler.updateView();   
        ///////////////////////////////////////////////////////////////////
              
                                }
                        });
                });
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
              
             
        <script type="text/javascript">
        var url;
        function newUser(){
            \$('#dlg_teacher').dialog('open').dialog('center').dialog('setTitle','Новый преподаватель');
            \$('#fm_teacher').form('clear');
            \$('.edits').empty();
            \$('.inputs').empty();
            url = 'insert_teacher.cgi?SID=$SID';
        }
        function editUser(){
            var row = \$('#dg').datagrid('getSelected');
            if (row){
	    \$('#dlg_teacher').dialog('open').dialog('center').dialog('setTitle','Редактирование преподавателя');
            \$('.edits').empty();
            \$('#fm_teacher').form('load',row);                           
            \$('.inputs').empty();            
            var uidd = row.UUID_IND;
            \$.ajax({
            type: 'GET',
            url: 'get_children.cgi?SID=$SID',
            cache: false,
            data: { 'uid': uidd },
            success: function(res1) {                                       
                                      for (var j=0; j<=res1.length-1; j++) 
                                      {                                       
                                       var rr = \$('<div>    <div class="fitem"><label><b>Ребенок:</b></label>  <div class="fitem"><label>ФИО ребенка:</label> <input name="DATA_CHILD_EDIT" value="' + res1[j].FIO + '" class="easyui-textbox"></div>   <div class="fitem"><label>Дата рождения:</label>  <input name="DATA_CHILD_EDIT" value="' + res1[j].DATE_OF_BORN + '" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser"></div>   <div class="fitem"><label>Пометить для удаления</label><input name="MARK_4_DEL" class="easyui-switchbutton" value="' + res1[j].ID + '" style="width:45px;height:15px"></div> <input type="hidden" name="DATA_CHILD_EDIT" value="' + res1[j].ID + '">     <hr />  </div>').fadeIn('slow').appendTo('.edits'); 
                                       \$.parser.parse(rr);
                                      } 
                                    },
            error: function() {alert("did not work");}
            });         
            url = 'edit_teacher.cgi?SID=$SID&uid='+uidd+'&idd='+row.ID;
            }
        }
        
        function saveUser() {
        var msg   = \$('#fm_teacher').serialize();
        \$.ajax({
          type: 'GET',
          url: url,
          data: msg,
          success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result=="Преподаватель отредактирован успешно!") {\$('#fm_teacher').form('clear'); \$('#dlg_teacher').dialog('close'); \$('#dg').datagrid('reload');}  if (res.result=="Преподаватель добавлен успешно!") {\$('#fm_teacher').form('clear'); \$('#dlg_teacher').dialog('close'); \$('#dg').datagrid('reload');}  if (res.result=="Преподаватель и его дети добавлены успешно!") {\$('#fm_teacher').form('clear'); \$('#dlg_teacher').dialog('close'); \$('#dg').datagrid('reload');} }, 
          
          error: function() {alert("did not work");}        
        });
           
       }
                
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
    
        <script type="text/javascript"> //Инициируем календарь
	function init() {
		scheduler.config.xml_date="%Y-%m-%d %H:%i";
		scheduler.config.prevent_cache = true;
		scheduler.config.details_on_create = true;
		scheduler.config.details_on_dblclick = true;
		scheduler.config.show_loading = true;
		scheduler.config.separate_short_events = true;
		scheduler.config.touch = "force";
		scheduler.config.readonly = true;
		scheduler.config.readonly_form = true;
				
		scheduler.config.lightbox.sections = [
				{name:"Описание события", height:130, map_to:"text", type:"textarea" , focus:true},
				{name:"Подробности", height:43, type:"textarea", map_to:"details" },
				{name:"time", height:72, type:"time", map_to:"auto"}
			];
	
		scheduler.init('scheduler_here',new Date(),"month");
		scheduler.setLoadMode("month");
		
                                     scheduler.templates.event_bar_date = function(start,end,ev){
                                     return "• <b>"+scheduler.templates.event_date(start)+" - "+scheduler.templates.event_date(end)+"</b> ";
                                     };	
        	
		
	}
        </script>
        
        <script> //Динамическое добавление полей для ввода инфы по детям
        \$(function(){
             
             var i=0;
             //Добавление            
            \$('html').on('click','.add',function () {
            var ff = \$('<div>    <div class="fitem"><label><b>Ребенок:</b></label>  <div class="fitem"><label>ФИО ребенка:</label> <input name="DATA_CHILD" class="easyui-textbox"></div>   <div class="fitem"><label>Дата рождения:</label>  <input name="DATA_CHILD" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser"></div>    <span class="remove"><a href="#">Удалить</a></span> <hr />  </div>').fadeIn('slow').appendTo('.inputs');            
            \$.parser.parse(ff);
            i++;
            if (i>0) {\$('#add').linkbutton({iconCls: 'icon-add', text: 'Добавить еще'});}
            });
            
            //Удаление
            \$('html').on('click','.remove', function () {                               
            \$(this).parent().remove();
            i--;
            if (i<1) {\$('#add').linkbutton({iconCls: 'icon-add', text: 'Добавить'});}
            });
    
            
        });
        </script>
		
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
		
		<script>
        function open_window_change_psw(){
           \$('#fm_change_psw').form('clear');
           \$('#g_psw').text("");
           \$('#g_psw').hide();
           \$('#USER_PSW1').textbox('clear');
           \$('#USER_PSW2').textbox('clear');
           \$('#dlg_change_psw').dialog('open').dialog('center').dialog('setTitle','Добавление/Изменение пароля преподавателя');
        }
        </script>
        
        <script>
        function change_psw() {
        var row1 = \$('#dg').datagrid('getSelected');
        if (row1)
        {
           var msg   = \$('#fm_change_psw').serialize();
           \$.ajax({
           type: 'GET',
           url: 'change_psw_teacher.cgi?SID=$SID&id_u='+row1.ID,
           data: msg,
           success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result) {\$('#fm_change_psw').form('clear'); \$('#dlg_change_psw').dialog('close');}  }, 
           error: function() {alert("did not work");}        
        });
        }   
       }
                
       </script>
       
       <script>
       ////////////////Генератор паролей
       function pass_gen(len) {
            var length = (len)?(len):(10);
            var string = "abcdefghijklmnopqrstuvwxyz"; 
            var numeric = '0123456789';
            var punctuation = '@#\$%!';
            var password = "";
            var character = "";
            var crunch = true;
            while( password.length<length ) {
                entity1 = Math.ceil(string.length * Math.random()*Math.random());
                entity2 = Math.ceil(numeric.length * Math.random()*Math.random());
                entity3 = Math.ceil(punctuation.length * Math.random()*Math.random());
                hold = string.charAt( entity1 );
                hold = (entity1%2==0)?(hold.toUpperCase()):(hold);
                character += hold;
                character += numeric.charAt( entity2 );
                character += punctuation.charAt( entity3 );
                password = character;
            }
            return password;
       }
       //////////////////////////////////////// 
        
       
       function get_gen_psw() {
          var created_psw = pass_gen();
          \$('#g_psw').text("Пароль: "+created_psw);
          \$('#USER_PSW1').textbox('setValue', created_psw);
          \$('#USER_PSW2').textbox('setValue', created_psw);
          \$('#g_psw').show();        
          
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
        <div data-options="region:'east',split:true,title:'Подробности'" style="width:30%;padding:1px;">

        <!--Панель TABS -->
        <div class="easyui-tabs" style="width:100%; height:auto;" data-options="narrow:true, fit:true">
         <div title="Общие">
         <table id="pg" style="width:100%"></table>
         </div>
         <div title="Занятия">
         </div>
         <div title="Свободное время"">
         </div>         
         <div title="Календарь">
         
          <!-- Календарь -->
           <div id="scheduler_here" class="dhx_cal_container" style="width:100%; height:100%">
                <div class="dhx_cal_navline">
                  <div class="dhx_cal_prev_button">&nbsp;</div>
                  <div class="dhx_cal_next_button">&nbsp;</div>
                  <div class="dhx_cal_today_button" style="width:60px"></div>
                  <div class="dhx_cal_date"></div>
                  <div class="dhx_cal_tab" name="day_tab" style="right:204px;"></div>
                  <div class="dhx_cal_tab" name="week_tab" style="right:140px;"></div>
                  <div class="dhx_cal_tab" name="month_tab" style="right:76px;"></div>
                  <div class="dhx_cal_tab" name="year_tab" style="right:268px; width:20px"></div>
               </div>
               <div class="dhx_cal_header"></div>
               <div class="dhx_cal_data"></div>
           </div>        
           <!-- Конец Календарь -->
         
         </div>
         <div title="Профиль">
         </div>
         <div title="Мультимедиатека">
         </div>
         <div title="Документы">
         </div>
        </div>
        <!-- Конец Панель TABS -->

        </div>
        <!-- Конец Правый DIV раздел подробности -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->

        <!-- Центральный DIV -рабочая область -->
        <div data-options="region:'center',title:'Рабочая область - Преподаватели. Пользователь: $formLogin'">

        <table id="dg" title="Преподаватели" class="easyui-datagrid" style="width:100%;height:95%"
        method="get"
        url="get_teachers.cgi?SID=$SID"
        toolbar="#tb, #toolbar"
        rownumbers="true" fitColumns="true" singleSelect="true" pagination="true" sortName="FIO" sortOrder="asc">

        <thead>
        <tr>         
            <th field="FIO" width="142" sortable="true">ФИО</th>
            <th field="POSITION" width="30">Должность</th>
            <th field="PHONE" width="20">Телефон</th>
            <th field="EMAIL" width="40">EMAIL</th>
        </tr>
        </thead>
        </table>
        <div id="toolbar">
        <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="newUser()">Добавить преподавателя</a>
        <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="editUser()">Редактировать преподавателя</a>
		<a href="#" class="easyui-linkbutton" iconCls="icon-document" plain="true" onclick="open_window_change_psw()">Создать/Сменить пароль</a>
        </div>

        <!-- Панель посика -->
        <div id="tb" style="padding:3px">
             <span>Поиск по ФИО:</span>
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
    
    
    <!-- Форма добавления нового преподавателя -->    
    <div id="dlg_teacher" class="easyui-dialog" style="width:530px;height:600px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons_teacher" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Информация о преподавателе</div>
        <form id="fm_teacher" novalidate>         
         <div class="fitem">
               <label>ФИО преподавателя:</label>
               <input name="FIO" class="easyui-textbox" required missingMessage="Данное поле необходимо заполнить">
	        </div>
	 <div class="fitem">
       	        <label>Должность:</label>
           	<input name="POSITION" class="easyui-textbox" required missingMessage="Данное поле необходимо заполнить">
           	</div>
         <div class="fitem">
               	<label>Телефон:</label>
               	<input name="PHONE" class="easyui-textbox" required missingMessage="Данное поле необходимо заполнить">
	        </div>
	 <div class="fitem">
               	<label>EMAIL:</label>
               	<input name="EMAIL" class="easyui-validatebox textbox" data-options="validType:'email'">
	        </div>
	 <div class="fitem">
               	<label>Дата рождения:</label>
               	<input name="DATE_OF_BORN" class="easyui-datebox" data-options="required:true, formatter:myformatter, parser:myparser" missingMessage="Данное поле необходимо заполнить">
	        </div>
	 <div class="fitem">
               	<label>Серия паспорта:</label>
               	<input name="SER_PASSPORT" class="easyui-textbox" data-options="required:true" missingMessage="Данное поле необходимо заполнить">
	        </div>
	 <div class="fitem">
               	<label>Номер паспорта:</label>
               <input name="NUM_PASSPORT" class="easyui-textbox" data-options="required:true" missingMessage="Данное поле необходимо заполнить">
           	</div>
         <div class="fitem">
               <label>Кем выдан:</label>
               <input name="KEM_VIDAN" class="easyui-textbox" data-options="required:true" missingMessage="Данное поле необходимо заполнить">
	        </div>
	 <div class="fitem">
               	<label>Когда выдан:</label>
               	<input name="KOGDA_VIDAN" class="easyui-datebox" data-options="required:true, formatter:myformatter, parser:myparser" missingMessage="Данное поле необходимо заполнить">
	        </div>
	 <div class="fitem">
               	<label>Код подразделения:</label>
               	<input name="KOD_PODRAZDELEN" class="easyui-textbox">
	        </div>
	 <div class="fitem">
               	<label>ИНН:</label>
               	<input name="INN" class="easyui-numberbox">
	        </div>
	 <div class="fitem">
               	<label>СНИЛС:</label>
               	<input name="SNILS" class="easyui-textbox">
	        </div>         
         <div class="fitem">
               	<label>Домашний адрес:</label>
               	<input name="HOME_ADDRESS" class="easyui-textbox" data-options="required:true" missingMessage="Данное поле необходимо заполнить">
	        </div>
	 <div class="fitem">
               	<label>Дата трудового договора:</label>
               	<input name="DATE_WORK_DOGOVOR" class="easyui-datebox" data-options="required:true, formatter:myformatter, parser:myparser" missingMessage="Данное поле необходимо заполнить">
                          </div>		 
	 <div class="fitem">
               	<label>Согласие на получение E-mail:</label>
               	<input name="AGREMMENT_GET_EMAIL" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>	
	 <div class="fitem ad">
               	<label><b>Информация о детях.</b></label>
                </div>	
	 <div class="fitem ad">
                <span class="addField add">
                <a href="#" id="add" class="easyui-linkbutton" data-options="iconCls:'icon-add'">Добавить</a>
                </span>               
               	</div>	 
               	<!-- Добавление инфы по детям -->
                <div class="inputs">               
                </div>
                <!-- Конец Добавление инфы по детям -->
                
                <!-- Поля для редактирования инфы по детям -->
                <div class="edits">               
                </div>
                <!-- Конец Поля для редактирования инфы по детям -->
        </form>
    </div>
    <div id="dlg-buttons_teacher">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="saveUser()" style="width:100px">Сохранить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript: \$('#dlg_teacher').dialog('close');" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма добавления нового преподавателя -->
	
	<!-- Форма изменения пароля препода -->    
    <div id="dlg_change_psw" class="easyui-dialog" style="width:500px;height:210px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons_change_psw" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Новый пароль преподавателя</div>
        <form id="fm_change_psw" novalidate>              
         <div class="fitem">
               <label>Пароль:</label>
               <input id="USER_PSW1" name="USER_PSW1" type="password" class="easyui-textbox">
	        </div>
	 <div class="fitem">
       	        <label>Еще раз:</label>
           	<input id="USER_PSW2" name="USER_PSW2" type="password" class="easyui-textbox">
           	</div>
        </form>
        <span id="g_psw" style="float:left; color: #F00; font-weight: bold;"></span>
    </div>
    <div id="dlg-buttons_change_psw">
        <a href="#" class="easyui-linkbutton" iconCls="icon-more" onclick="get_gen_psw()" style="float:left;">Сгенерировать пароль</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="change_psw()" style="width:100px">Ок</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript: \$('#dlg_change_psw').dialog('close')" style="width:90px">Отменить</a>        
    </div>
    <!-- Конец Форма изменения пароля препода -->
    
    
    
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