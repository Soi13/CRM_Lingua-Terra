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
my $DOCUMENTS_SEKRETARIAT=$sess->param('DOCUMENTS_SEKRETARIAT');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

    if ($DOCUMENTS_SEKRETARIAT==1) #Смотрим имеет ли доступ пользователь к модулю "Документы".
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
        <link rel="stylesheet" href="../CSS/styles.css">        
        
        <script type="text/javascript" src="../JS/jquery.min.js"></script>
        <script type="text/javascript" src="../JS/jquery.easyui.min.js"></script>
        <script src="../JS/script.js"></script>
        <script src="../ckeditor/ckeditor.js"></script>
        <script src="../ckeditor/adapters/jquery.js"></script>        
               
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
       
       <script type="text/javascript"> ////////////Работа с шаблонами договоров
        var url;
        function newTemplate(){
            \$('#dlg_template').dialog('open').dialog('center').dialog('setTitle','Новый шаблон');
            \$('#fm').form('clear');      
            \$('#TEXT_OF_DOCUMENT').val(''); 
            \$('#SID').val('$SID');
            url = 'insert_template.cgi'; 
        }
        function editTemplate(){
            var row = \$('#dg').datagrid('getSelected');
            if (row){
	    \$('#dlg_template').dialog('open').dialog('center').dialog('setTitle','Редактирование шаблона');
            \$('#fm').form('load',row);        
            \$('#id_x').val(row.ID);       
            \$('#SID').val('$SID');
            url = 'edit_template.cgi';                                          
            }
        }
        
        function saveTemplate() {
        var msg   = \$('#fm').serialize();
        \$.ajax({
          type: 'POST',
          url: url,
          data: msg,
          success: function(res) { \$.messager.alert('Информация',res.result,'info'); if (res.result=="Шаблон добавлен успешно!") {\$('#fm').form('clear'); \$('#dlg_template').dialog('close'); \$('#dg').datagrid('reload');} if (res.result=="Шаблон отредактирован успешно!") {\$('#fm').form('clear'); \$('#dlg_template').dialog('close'); \$('#dg').datagrid('reload');}},
          error: function() {alert("did not work");}
        });        
       }
                
    </script>///////////////////////////////
	
	<script type="text/javascript"> ////////////Работа с шаблонами ордеров
        var url_order;
        function newTemplate_order(){
            \$('#dlg_template_order').dialog('open').dialog('center').dialog('setTitle','Новый шаблон');
            \$('#fm_order').form('clear');      
            \$('#TEXT_OF_DOCUMENT_order').val(''); 
            \$('#SID_order').val('$SID');
            url_order = 'insert_template.cgi'; //?SID=$SID';
        }
        function editTemplate_order(){
            var row = \$('#dg_order').datagrid('getSelected');
            if (row){
	    \$('#dlg_template_order').dialog('open').dialog('center').dialog('setTitle','Редактирование шаблона');
            \$('#fm_order').form('load',row);        
            \$('#id_x_order').val(row.ID);       
            \$('#SID_order').val('$SID');
            url_order = 'edit_template.cgi'; //?id_x='+row.ID+'&SID=$SID';                                          
            }
        }
        
        function saveTemplate_order() {
        var msg   = \$('#fm_order').serialize();
        \$.ajax({
          type: 'POST',
          url: url_order,
          data: msg,
          success: function(res) { \$.messager.alert('Информация',res.result,'info'); if (res.result=="Шаблон добавлен успешно!") {\$('#fm_order').form('clear'); \$('#dlg_template_order').dialog('close'); \$('#dg_order').datagrid('reload');} if (res.result=="Шаблон отредактирован успешно!") {\$('#fm_order').form('clear'); \$('#dlg_template_order').dialog('close'); \$('#dg_order').datagrid('reload');}},
          error: function() {alert("did not work");}
        });        
       }
                
    </script>////////////////////////////////
    
    <script> //Подключение компонента ckeditor вместо TEXAREA
    \$(function(){                 
       \$('#TEXT_OF_DOCUMENT').ckeditor({uiColor:'#FDE0B0', fullPage:true});  
	   \$('#TEXT_OF_DOCUMENT_order').ckeditor({uiColor:'#FDE0B0', fullPage:true}); 
                 })
    </script>    
    
    
        </head>
 
 
        <body class="easyui-layout" onload="init()";>
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
        <!--<div data-options="region:'east',split:true,title:'Подробности'" style="width:30%;padding:1px;"></div> -->
        <!-- Конец Правый DIV раздел подробности -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->

        <!-- Центральный DIV -рабочая область -->
        <div data-options="region:'center',title:'Рабочая область - Документы. Пользователь: $formLogin'">

        <!-- Компонент Accordion в котором будут размещаться все документы -->        
        <div class="easyui-accordion" style="width:auto;height:100%">
        
        <div title="Шаблоны договоры студентов" style="overflow:auto; padding:10px;">        
        <table id="dg" class="easyui-datagrid" style="width:100%;height:100%"
        method="get"
        url="get_dogovor_templates.cgi?SID=$SID"
        toolbar="#toolbar"
        fitColumns="true" singleSelect="true" sortName="KIND_DOCUMENT" sortOrder="asc">

        <thead>
        <tr>
            <th field="ID" width="15" sortable="true" hidden="true">ID1</th>
            <th field="KND_DOC" width="50" sortable="true">Вид договора</th>                        
            <th field="NAIMENOVAN_DOCUMENT" width="100" sortable="true">Наименование документа</th>
            <th field="DESCRIPTION_DOCUMENT" width="100" sortable="true">Описание документа</th>                        
            
        </tr>
        </thead>
        
        </table>
        <div id="toolbar">
        <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="newTemplate()">Добавить шаблон</a>
        <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="editTemplate()">Редактировать шаблон</a>
        </div>
        </div>
        
        <div title="Шаблоны сертификатов студентов" style="overflow:auto;padding:10px;">
        </div>
        
        <div title="Шаблоны договоров КА" style="overflow:auto;padding:10px;">
        </div>
        
        <div title="Шаблоны счетов для договоров КА" style="overflow:auto;padding:10px;">
        </div>
        
        <div title="Шаблоны ордеров" style="overflow:auto;padding:10px;">
        
        <table id="dg_order" class="easyui-datagrid" style="width:100%;height:100%"
        method="get"
        url="get_order_templates.cgi?SID=$SID"
        toolbar="#toolbar1"
        fitColumns="true" singleSelect="true" sortName="KIND_DOCUMENT" sortOrder="asc">

        <thead>
        <tr>
            <th field="ID" width="15" sortable="true" hidden="true">ID1</th>
            <th field="KND_DOC" width="50" sortable="true">Вид договора</th>                        
            <th field="NAIMENOVAN_DOCUMENT" width="100" sortable="true">Наименование документа</th>
            <th field="DESCRIPTION_DOCUMENT" width="100" sortable="true">Описание документа</th>                        
            
        </tr>
        </thead>
        
        </table>
        <div id="toolbar1">
        <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="newTemplate_order()">Добавить шаблон</a>
        <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="editTemplate_order()">Редактировать шаблон</a>
        </div>
        
        </div>	
		
		</div>
        <!-- Конец Компонент Accordion в котором будут размещаться все документы -->        
        
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
    
    <!-- Форма добавления нового шаблона договора -->    
    <div id="dlg_template" class="easyui-dialog" style="width:850px;height:650px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Создание шаблона</div>
        <form id="fm" novalidate>
            <div class="fitem">
               	<label>Тип документа:</label>
               	<input name="TYPE_DOCUMENT" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_type_docs.cgi?SID=$SID', method: 'get'" missingMessage="Данное поле необходимо заполнить">
           	</div>
            <div class="fitem">
               	<label>Вид документа:</label>
               	<input name="KIND_DOCUMENT" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_kind_docs.cgi?SID=$SID', method: 'get'" missingMessage="Данное поле необходимо заполнить">
           	</div>
            <div class="fitem">
               	<label>Наименование документа:</label>
               	<input name="NAIMENOVAN_DOCUMENT" class="easyui-textbox" required missingMessage="Данное поле необходимо заполнить">
	        </div>            
            <div class="fitem">
               	<label>Описание документа:</label>
               	<input name="DESCRIPTION_DOCUMENT" class="easyui-textbox" data-options="multiline:true" style="height:100px">
	        </div>
	    <div class="fitem">
	        <label>Тэги для создания шаблонов:</label>
	        <p>
	        <span class="lab"><a href="#">%НОМЕР_ДОГОВОРА%</a></span> <span class="lab"><a href="#">%ДАТА_НАЧАЛА_ДОГОВОРА%</a></span> <span class="lab"><a href="#">%ДАТА_ОКОНЧАНИЯ_ДОГОВОРА%</a></span> <span class="lab"><a href="#">%ВИД_ПРОГРАММЫ%</a></span>
	        <span class="lab"><a href="#">%ФИО_СТУДЕНТА%</a></span> <span class="lab"><a href="#">%ФИО_РОДИТЕЛЯ_СТУДЕНТА%</a></span> <span class="lab"><a href="#">%ДОМ_АДРЕС%</a></span> <span class="lab"><a href="#">%МОБ_ТЕЛЕФОН%</a></span>
	        </p>       
	        </div>        
	    <div class="fitem">
               	<label>Текст документа:</label>
               	<textarea name="TEXT_OF_DOCUMENT" id="TEXT_OF_DOCUMENT" rows="10" cols="80">
               	</textarea>               
	        </div>
	        
	        <input name="SID" id="SID" type="hidden" value="">
	        <input name="id_x" id="id_x" type="hidden" value="">                 
        </form>
    </div>
    <div id="dlg-buttons">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="saveTemplate()" style="width:100px">Сохранить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_template').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма добавления нового шаблона договора -->
	
	<!-- Форма добавления нового шаблона ордера -->    
    <div id="dlg_template_order" class="easyui-dialog" style="width:850px;height:650px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons_order" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Создание шаблона</div>
        <form id="fm_order" novalidate>
            <div class="fitem">
               	<label>Тип документа:</label>
               	<input name="TYPE_DOCUMENT" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_type_docs.cgi?SID=$SID', method: 'get'" missingMessage="Данное поле необходимо заполнить">
           	</div>
            <div class="fitem">
               	<label>Вид документа:</label>
               	<input name="KIND_DOCUMENT" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_kind_docs.cgi?SID=$SID', method: 'get'" missingMessage="Данное поле необходимо заполнить">
           	</div>
            <div class="fitem">
               	<label>Наименование документа:</label>
               	<input name="NAIMENOVAN_DOCUMENT" class="easyui-textbox" required missingMessage="Данное поле необходимо заполнить">
	        </div>            
            <div class="fitem">
               	<label>Описание документа:</label>
               	<input name="DESCRIPTION_DOCUMENT" class="easyui-textbox" data-options="multiline:true" style="height:100px">
	        </div>
	    <div class="fitem">
	        <label>Тэги для создания шаблонов:</label>
	        <p>
	        <span class="lab"><a href="#">%НОМЕР_ДОГОВОРА%</a></span> <span class="lab"><a href="#">%ДАТА_НАЧАЛА_ДОГОВОРА%</a></span> <span class="lab"><a href="#">%ДАТА_ОКОНЧАНИЯ_ДОГОВОРА%</a></span> <span class="lab"><a href="#">%ВИД_ПРОГРАММЫ%</a></span>
	        <span class="lab"><a href="#">%ФИО_СТУДЕНТА%</a></span> <span class="lab"><a href="#">%ДАТА_РОЖДЕНИЯ_СТУДЕНТА%</a></span> <span class="lab"><a href="#">%ФИО_РОДИТЕЛЯ_СТУДЕНТА%</a></span> <span class="lab"><a href="#">%ДОМ_АДРЕС%</a></span> <span class="lab"><a href="#">%МОБ_ТЕЛЕФОН%</a></span>
	        <span class="lab"><a href="#">%ПОЛНАЯ СТОИМОСТЬ_КУРСА%</a></span> <span class="lab"><a href="#">%СЕРИЯ_ПАСПОРТА_СТУДЕНТА%</a></span> <span class="lab"><a href="#">%НОМЕР_ПАСПОРТА_СТУДЕНТА%</a></span> <span class="lab"><a href="#">%КЕМ_ВЫДАН_ПАСПОРТ_СТУДЕНТА%</a></span>
	        <span class="lab"><a href="#">%КОГДА_ВЫДАН_ПАСПОРТ_СТУДЕНТА%</a></span> <span class="lab"><a href="#">%ДАТА_РОЖДЕНИЯ_СТУДЕНТА%</a></span> <span class="lab"><a href="#">%СЕРИЯ_ПАСПОРТА_РОДИТЕЛЯ%</a></span> <span class="lab"><a href="#">%НОМЕР_ПАСПОРТА_РОДИТЕЛЯ%</a></span>
	        <span class="lab"><a href="#">%КЕМ_ВЫДАН_ПАСПОРТ_РОДИТЕЛЯ%</a></span> <span class="lab"><a href="#">%КОГДА_ВЫДАН_ПАСПОРТ_РОДИТЕЛЯ%</a></span> <span class="lab"><a href="#">%СТОИМОСТЬ ОБУЧЕНИЯ%</a></span>
	        </p>       
	        </div>        
	    <div class="fitem">
               	<label>Текст документа:</label>
               	<textarea name="TEXT_OF_DOCUMENT" id="TEXT_OF_DOCUMENT_order" rows="10" cols="80">
               	</textarea>               
	        </div>
	        
	        <input name="SID" id="SID_order" type="hidden" value="">
	        <input name="id_x" id="id_x_order" type="hidden" value="">                 
        </form>
    </div>
    <div id="dlg-buttons_order">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="saveTemplate_order()" style="width:100px">Сохранить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_template_order').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма добавления нового шаблона ордера -->
       
    
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