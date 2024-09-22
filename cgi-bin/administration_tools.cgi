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
my $OPTIONS_SUPERADMIN=$sess->param('OPTIONS_SUPERADMIN');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

    if ($OPTIONS_SUPERADMIN==1) #Смотрим имеет ли доступ пользователь к модулю "Настройки Суперадмина".
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
		<script type="text/javascript" src="../JS/datagrid-groupview.js"></script>
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
              
        
       <script>  //Схлопываем все разделы в accordion
       \$(function(){
           var panels = \$('#acc').accordion('panels');
           \$.map(panels, function(p){
	   p.panel('collapse');
           })        
       });
       </script>
       
       <script>
       function doSearch(){
       \$('#dg').datagrid('load',{
       login: \$('#login').textbox('getText'),
       full_name: \$('#full_name').textbox('getText')
       });
       }
	   
	   function doSearch_branch(){
       \$('#dg_branches').datagrid('load',{
       branch_name: \$('#branch_name').textbox('getText')
       });
       }
	   
	   function doSearch_source(){
       \$('#dg_source_about_us').datagrid('load',{
       source_name: \$('#source_name').textbox('getText')
       });
       }
	   
	   function doSearch_person_get_zayav(){
       \$('#dg_who_get_zayav').datagrid('load',{
       usr_name: \$('#usr_name').textbox('getText')
       });
       }
	   
	   function doSearch_course(){
       \$('#dg_course').datagrid('load',{
       course_name: \$('#course_name').textbox('getText')
       });
       }
	   
	   function doSearch_level_lang(){
       \$('#dg_level_lang').datagrid('load',{
       level_lang_name: \$('#level_lang_name').textbox('getText')
       });
       }
	   
	   function doSearch_source_zayav(){
       \$('#dg_source_zayav').datagrid('load',{
       source_zayav_name: \$('#source_zayav_name').textbox('getText')
       });
       }
	   
	   function doSearch_prog(){
       \$('#dg_prog').datagrid('load',{
       prog_name: \$('#prog_name').textbox('getText')
       });
       }
	   
	   function doSearch_type_group(){
       \$('#dg_type_group').datagrid('load',{
       type_group_name: \$('#type_group_name').textbox('getText')
       });
       }
	   
	   function doSearch_teacher(){
       \$('#dg_teachers').datagrid('load',{
       fio_teacher: \$('#fio_teacher').textbox('getText')
       });
       }
	   
	   function doSearch_event(){
       \$('#dg_events').datagrid('load',{
       event_name: \$('#event_name').textbox('getText')
       });
       }
       </script>
       
       <script>
       \$(function(){
       \$('#dg').datagrid({
       onSelect:function(index){
       var row = \$('#dg').datagrid('getSelected');
       //Загружаем и заполняем подробности по пользователю
       \$('#pg').propertygrid({
       method:'get',
       url: 'get_users_detail.cgi?id='+row.ID+'&SID=$SID',
       showGroup: true,
       showHeader: false,
       scrollbarSize: 0,
       nowrap: false
       });
       //////////////////////////////////////////
                               }
                        });
                });
        </script>
       
       
       
       
        <script> //Возможность поиска по нажатию Enter
        \$(document).ready(function(){
	var t = \$('#login');
	var n = \$('#full_name');
	
	////////////
	t.textbox('textbox').bind('keydown', function(e){
	   if (e.keyCode == 13) 
	   { 
	      doSearch();
	   }
	});	
	
	///////////
	n.textbox('textbox').bind('keydown', function(e){
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
        \$('#login').textbox({
	                      inputEvents:\$.extend({},\$.fn.textbox.defaults.inputEvents,{
		              keyup:function(e){
			                          doSearch();
		                               }
	                      })
                           })
        
        
        //Добавление полю NumberBox события KeyUp для поиска на лету
        \$('#full_name').textbox({
	                      inputEvents:\$.extend({},\$.fn.numberbox.defaults.inputEvents,{
		              keyup:function(e){
			                          doSearch();
		                               }
	                      })
                           })


        //Добавление полю TextBox события KeyUp для поиска на лету
        \$('#branch_name').textbox({
	                      inputEvents:\$.extend({},\$.fn.textbox.defaults.inputEvents,{
		              keyup:function(e){
			                          doSearch_branch();
		                               }
	                      })
                           })
						   

        //Добавление полю TextBox события KeyUp для поиска на лету
        \$('#source_name').textbox({
	                      inputEvents:\$.extend({},\$.fn.textbox.defaults.inputEvents,{
		              keyup:function(e){
			                          doSearch_source();
		                               }
	                      })
                           })	

        //Добавление полю TextBox события KeyUp для поиска на лету
        \$('#usr_name').textbox({
	                      inputEvents:\$.extend({},\$.fn.textbox.defaults.inputEvents,{
		              keyup:function(e){
			                          doSearch_person_get_zayav();
		                               }
	                      })
                           })

        //Добавление полю TextBox события KeyUp для поиска на лету
        \$('#course_name').textbox({
	                      inputEvents:\$.extend({},\$.fn.textbox.defaults.inputEvents,{
		              keyup:function(e){
			                          doSearch_course();
		                               }
	                      })
                           })	

        //Добавление полю TextBox события KeyUp для поиска на лету
        \$('#level_lang_name').textbox({
	                      inputEvents:\$.extend({},\$.fn.textbox.defaults.inputEvents,{
		              keyup:function(e){
			                          doSearch_level_lang();
		                               }
	                      })
                           })	

        //Добавление полю TextBox события KeyUp для поиска на лету
        \$('#source_zayav_name').textbox({
	                      inputEvents:\$.extend({},\$.fn.textbox.defaults.inputEvents,{
		              keyup:function(e){
			                          doSearch_source_zayav();
		                               }
	                      })
                           })
						
		//Добавление полю TextBox события KeyUp для поиска на лету
        \$('#prog_name').textbox({
	                      inputEvents:\$.extend({},\$.fn.textbox.defaults.inputEvents,{
		              keyup:function(e){
			                          doSearch_prog();
		                               }
	                      })
                           })
						   
		//Добавление полю TextBox события KeyUp для поиска на лету
        \$('#type_group_name').textbox({
	                      inputEvents:\$.extend({},\$.fn.textbox.defaults.inputEvents,{
		              keyup:function(e){
			                          doSearch_type_group();
		                               }
	                      })
                           })  
		
		//Добавление полю TextBox события KeyUp для поиска на лету
        \$('#fio_teacher').textbox({
	                      inputEvents:\$.extend({},\$.fn.textbox.defaults.inputEvents,{
		              keyup:function(e){
			                          doSearch_teacher();
		                               }
	                      })
                           })

        //Добавление полю TextBox события KeyUp для поиска на лету
        \$('#event_name').textbox({
	                      inputEvents:\$.extend({},\$.fn.textbox.defaults.inputEvents,{
		              keyup:function(e){
			                          doSearch_event();
		                               }
	                      })
                           })						   
        
        })
        </script>
        
               
        <script>
        function formatStatus(val,row){
            if (val == 1){
                return '<span style="color:green; font-weight:bold;">Активный</span>';
            } else {
                return '<span style="color:red; font-weight:bold;">Заблокирован</span>';
            }
        }
                
        function formatAdm(val,row){
            if (val == 1){
                return '<span>Да</span>';
            } else {
                return '<span>Нет</span>';
            }
        }
		
		function format_branch(val,row){
            if (val == 1){
                return '<span style="color:red; font-weight:bold;">Скрыт</span>';
            } else {
                return '<span style="color:green; font-weight:bold;">Доступен</span>';
            }
        }
		
		function format_source(val,row){
            if (val == 1){
                return '<span style="color:red; font-weight:bold;">Скрыт</span>';
            } else {
                return '<span style="color:green; font-weight:bold;">Доступен</span>';
            }
        }
		
		function format_who_get_zayav(val,row){
            if (val == 1){
                return '<span style="color:red; font-weight:bold;">Скрыт</span>';
            } else {
                return '<span style="color:green; font-weight:bold;">Доступен</span>';
            }
        }
		
		function format_course(val,row){
            if (val == 1){
                return '<span style="color:red; font-weight:bold;">Скрыт</span>';
            } else {
                return '<span style="color:green; font-weight:bold;">Доступен</span>';
            }
        }
		
		function format_level_lang(val,row){
            if (val == 1){
                return '<span style="color:red; font-weight:bold;">Скрыт</span>';
            } else {
                return '<span style="color:green; font-weight:bold;">Доступен</span>';
            }
        }
		
		function format_source_zayav(val,row){
            if (val == 1){
                return '<span style="color:red; font-weight:bold;">Скрыт</span>';
            } else {
                return '<span style="color:green; font-weight:bold;">Доступен</span>';
            }
        }
		
		function format_prog(val,row){
            if (val == 1){
                return '<span style="color:red; font-weight:bold;">Скрыт</span>';
            } else {
                return '<span style="color:green; font-weight:bold;">Доступен</span>';
            }
        }
		
		function format_type_group(val,row){
            if (val == 1){
                return '<span style="color:red; font-weight:bold;">Скрыт</span>';
            } else {
                return '<span style="color:green; font-weight:bold;">Доступен</span>';
            }
        }
		
		function format_teachers(val,row){
            if (val == 1){
                return '<span style="color:red; font-weight:bold;">Скрыт</span>';
            } else {
                return '<span style="color:green; font-weight:bold;">Доступен</span>';
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
        
        <script>
        var url;
        function newUser(){
            \$('#dlg_new_user').dialog('open').dialog('center').dialog('setTitle','Новый пользователь');
            \$('#fm_user').form('clear');            
            \$('.sekretariat').switchbutton('disable')
            \$('.sekretariat').switchbutton('uncheck')
            \$('.finance').switchbutton('disable')
            \$('.finance').switchbutton('uncheck')
            \$('.registration').switchbutton('disable')
            \$('.registration').switchbutton('uncheck')
            \$('.e_learning').switchbutton('disable')
            \$('.e_learning').switchbutton('uncheck')
            \$('.multimediateka').switchbutton('disable')
            \$('.multimediateka').switchbutton('uncheck')
            \$('.superadmin').switchbutton('disable')
            \$('.superadmin').switchbutton('uncheck')
            \$('.reports').switchbutton('disable')
            \$('.reports').switchbutton('uncheck')
            \$('.ancets').switchbutton('disable')
            \$('.ancets').switchbutton('uncheck')
            \$('#PASSW_DAYS_OF_LIVE').numberbox('setValue', '40');
            url = 'insert_new_user.cgi?SID=$SID';
            
        }
        function editUser(){
            var row = \$('#dg').datagrid('getSelected');
            if (row){
	    \$('#fm_user').form('clear');
	    \$('.sekretariat').switchbutton('disable')
            \$('.sekretariat').switchbutton('uncheck')
            \$('.finance').switchbutton('disable')
            \$('.finance').switchbutton('uncheck')
            \$('.registration').switchbutton('disable')
            \$('.registration').switchbutton('uncheck')
            \$('.e_learning').switchbutton('disable')
            \$('.e_learning').switchbutton('uncheck')
            \$('.multimediateka').switchbutton('disable')
            \$('.multimediateka').switchbutton('uncheck')
            \$('.superadmin').switchbutton('disable')
            \$('.superadmin').switchbutton('uncheck')
            \$('.reports').switchbutton('disable')
            \$('.reports').switchbutton('uncheck')
            \$('.ancets').switchbutton('disable')
            \$('.ancets').switchbutton('uncheck')
	    \$('#dlg_new_user').dialog('open').dialog('center').dialog('setTitle','Редактирование пользователя');
            \$('#fm_user').form('load',row);               
            url = 'edit_user.cgi?id_x='+row.ID+'&SID=$SID';             
            }
        }
        
        function saveUser() {
        var msg   = \$('#fm_user').serialize();
        \$.ajax({
          type: 'GET',
          url: url,
          data: msg,
          success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result.substr(0,30)=="Пользователь добавлен успешно!") {\$('#fm_user').form('clear'); \$('#dlg_new_user').dialog('close'); \$('#dg').datagrid('reload');}  if (res.result=="Пользователь отредактирован успешно!") {\$('#fm_user').form('clear'); \$('#dlg_new_user').dialog('close'); \$('#dg').datagrid('reload');} }, 
          error: function() {alert("did not work");}        
        });
           
       }
                
       </script>
    
       <script>            
       \$(function(){        
        /////////////////////////////////////////////////
        \$('#TOP_SEKRETARIAT').switchbutton({                       
            onChange: function(checked){
                                          if(checked)
                                          { 
                                             \$('.sekretariat').switchbutton('enable')
                                             \$('.finance').switchbutton('enable')
                                          }
                                          else
                                          {
                                             \$('.sekretariat').switchbutton('uncheck')
                                             \$('.sekretariat').switchbutton('disable')
                                             \$('.finance').switchbutton('uncheck')
                                             \$('.finance').switchbutton('disable')                                             
                                          }
                                       }
                                            });                                        
        /////////////////////////////////////////////////
       
        /////////////////////////////////////////////////
        \$('#TOP_FINANCE').switchbutton({                       
            onChange: function(checked){
                                          if(checked)
                                          { 
                                             \$('.finance').switchbutton('enable')
                                          }
                                          else
                                          {
                                             \$('.finance').switchbutton('uncheck')
                                             \$('.finance').switchbutton('disable')                                             
                                          }
                                       }
                                         });                                        
        /////////////////////////////////////////////////
       
        /////////////////////////////////////////////////
        \$('#TOP_REGISTRATION').switchbutton({                       
            onChange: function(checked){
                                          if(checked)
                                          { 
                                             \$('.registration').switchbutton('enable')
                                          }
                                          else
                                          {
                                             \$('.registration').switchbutton('uncheck')
                                             \$('.registration').switchbutton('disable')
                                          }
                                       }
                                         });                                        
        /////////////////////////////////////////////////
        
        /////////////////////////////////////////////////
        \$('#TOP_E_LEARNING').switchbutton({                       
            onChange: function(checked){
                                          if(checked)
                                          { 
                                             \$('.e_learning').switchbutton('enable')
                                          }
                                          else
                                          {
                                             \$('.e_learning').switchbutton('uncheck')
                                             \$('.e_learning').switchbutton('disable')
                                          }
                                       }
                                         });                                        
        /////////////////////////////////////////////////
        
        /////////////////////////////////////////////////
        \$('#TOP_MULTIMEDIATEKA').switchbutton({                       
            onChange: function(checked){
                                          if(checked)
                                          { 
                                             \$('.multimediateka').switchbutton('enable')
                                          }
                                          else
                                          {
                                             \$('.multimediateka').switchbutton('uncheck')
                                             \$('.multimediateka').switchbutton('disable')
                                          }
                                       }
                                         });                                        
        /////////////////////////////////////////////////
        
         /////////////////////////////////////////////////
        \$('#TOP_SUPERADMIN').switchbutton({                       
            onChange: function(checked){
                                          if(checked)
                                          { 
                                             \$('.superadmin').switchbutton('enable')
                                          }
                                          else
                                          {
                                             \$('.superadmin').switchbutton('uncheck')
                                             \$('.superadmin').switchbutton('disable')
                                          }
                                       }
                                         });                                        
        /////////////////////////////////////////////////
        
        /////////////////////////////////////////////////
        \$('#TOP_REPORTS').switchbutton({                       
            onChange: function(checked){
                                          if(checked)
                                          { 
                                             \$('.reports').switchbutton('enable')
                                          }
                                          else
                                          {
                                             \$('.reports').switchbutton('uncheck')
                                             \$('.reports').switchbutton('disable')
                                          }
                                       }
                                         });                                        
        /////////////////////////////////////////////////
        
        /////////////////////////////////////////////////
        \$('#TOP_ANKETS').switchbutton({                       
            onChange: function(checked){
                                          if(checked)
                                          { 
                                             \$('.ancets').switchbutton('enable')
                                          }
                                          else
                                          {
                                             \$('.ancets').switchbutton('uncheck')
                                             \$('.ancets').switchbutton('disable')
                                          }
                                       }
                                         });                                        
        /////////////////////////////////////////////////
       
       
        });
        </script>
        
        
       <script>
       function activate_lock(){
            var row = \$('#dg').datagrid('getSelected');
            var mes;
            if (row.ACTIVE==1)
            {
               mes='Вы уверены, что необходимо заблокировать пользователя?';               
            }
            else
            {
               mes='Вы уверены, что необходимо разблокировать пользователя?'               
            }
            
            \$.messager.confirm('Внимание', mes,function(r){
                    if (r){
                             \$.ajax({            
                             type: 'GET',
                             traditional: true,
                             url: 'activate_lock_user.cgi?SID=$SID',
                             data: {'id_user':row.ID},
                             success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result) {\$('#dg').datagrid('reload'); \$('#dlg_new_user').dialog('close');}},
                             error: function() {alert("did not work");}
                             });
                     
                          }   
                  });
        }  
        </script>
        
        <script>
        function open_window_change_user_psw(){
           \$('#fm_change_psw_user').form('clear');
           \$('#g_psw').text("");
           \$('#g_psw').hide();
           \$('#USER_PSW1').textbox('clear');
           \$('#USER_PSW2').textbox('clear');
           \$('#dlg_change_psw_user').dialog('open').dialog('center').dialog('setTitle','Изменение пароля пользователя');           
        }
        </script>
        
        <script>
        function change_psw_user() {
        var row1 = \$('#dg').datagrid('getSelected');
        if (row1)
        {
           var msg   = \$('#fm_change_psw_user').serialize();
           \$.ajax({
           type: 'GET',
           url: 'change_psw_user.cgi?SID=$SID&id_u='+row1.ID,
           data: msg,
           success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result=="Пароль заменен успешно!") {\$('#fm_change_psw_user').form('clear'); \$('#dlg_change_psw_user').dialog('close');}  }, 
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
	   
	   <script>
        var url_branch;
        function newBranch(){
            \$('#dlg_new_branch').dialog('open').dialog('center').dialog('setTitle','Новый филиал');
            \$('#fm_branch').form('clear');
            url_branch = 'insert_new_branch.cgi?SID=$SID';            
        }
        
        function editBranch(){
            var row_br = \$('#dg_branches').datagrid('getSelected');
            if (row_br){
	    \$('#fm_branch').form('clear');
	    \$('#dlg_new_branch').dialog('open').dialog('center').dialog('setTitle','Редактирование филиала');
            \$('#fm_branch').form('load',row_br);               
            url_branch = 'edit_branch.cgi?id_br='+row_br.ID+'&SID=$SID';             
            }
        }
        
        function saveBranch() {
        var msg   = \$('#fm_branch').serialize();
        \$.ajax({
          type: 'GET',
          url: url_branch,
          data: msg,
          success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result=="Филиал добавлен успешно!") {\$('#fm_branch').form('clear'); \$('#dlg_new_branch').dialog('close'); \$('#dg_branches').datagrid('reload');}  if (res.result=="Филиал отредактирован успешно!") {\$('#fm_branch').form('clear'); \$('#dlg_new_branch').dialog('close'); \$('#dg_branches').datagrid('reload');} }, 
          error: function() {alert("did not work");}        
        });
           
       }
                
       </script>
	   
	   <script>
       function hideBranch(){
            var row_br = \$('#dg_branches').datagrid('getSelected');
            var mes_br;
            if (row_br.BLOCKED==1)
            {
               mes_br='Вы уверены, что необходимо сделать доступным филиал?';               
            }
            else
            {
               mes_br='Вы уверены, что необходимо скрыть филиал?'               
            }
            
            \$.messager.confirm('Внимание', mes_br, function(r){
                    if (r){
                             \$.ajax({            
                             type: 'GET',
                             traditional: true,
                             url: 'hide_branch.cgi?SID=$SID',
                             data: {'id_br':row_br.ID},
                             success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result) {\$('#dg_branches').datagrid('reload');}},
                             error: function() {alert("did not work");}
                             });
                     
                          }   
                  });
        }  
        </script>
				
		<script>
        function del_session(){
            var row_ses = \$('#dg_sessions').datagrid('getSelected');
            if (row_ses)
            {            
               \$.messager.confirm('Внимание', 'Вы уверены, что необходимо удалить сессию. Текущий сеанс пользователя будет отключен!', function(r){
                    if (r){
                             \$.ajax({            
                             type: 'GET',
                             traditional: true,
                             url: 'remove_session.cgi?SID=$SID',
                             data: {'id_ses':row_ses.id},
                             success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result) {\$('#dg_sessions').datagrid('reload');}},
                             error: function() {alert("did not work");}
                             });
                     
                          }   
                  });
                  
            }       
                  
        }  
        </script>
		
	    <script>
        var url_source;
        function newSource(){
            \$('#dlg_new_source_about_us').dialog('open').dialog('center').dialog('setTitle','Новый источник');
            \$('#fm_source_about_us').form('clear');
            url_source = 'insert_new_source.cgi?SID=$SID';            
        }
        
        function editSource(){
            var row_sr = \$('#dg_source_about_us').datagrid('getSelected');
            if (row_sr){
	    \$('#fm_source_about_us').form('clear');
	    \$('#dlg_new_source_about_us').dialog('open').dialog('center').dialog('setTitle','Редактирование источника');
            \$('#fm_source_about_us').form('load',row_sr);               
            url_source = 'edit_source.cgi?id_sr='+row_sr.ID+'&SID=$SID';             
            }
        }
        
        function saveSource() {
        var msg   = \$('#fm_source_about_us').serialize();
        \$.ajax({
          type: 'GET',
          url: url_source,
          data: msg,
          success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result=="Источник добавлен успешно!") {\$('#fm_source_about_us').form('clear'); \$('#dlg_new_source_about_us').dialog('close'); \$('#dg_source_about_us').datagrid('reload');}  if (res.result=="Источник отредактирован успешно!") {\$('#fm_source_about_us').form('clear'); \$('#dlg_new_source_about_us').dialog('close'); \$('#dg_source_about_us').datagrid('reload');} }, 
          error: function() {alert("did not work");}        
        });
           
       }
                
       </script>
       
       <script>
       function hideSource(){
            var row_sr = \$('#dg_source_about_us').datagrid('getSelected');
            var mes_sr;
            if (row_sr.BLOCKED==1)
            {
               mes_sr='Вы уверены, что необходимо сделать доступным источник?';               
            }
            else
            {
               mes_sr='Вы уверены, что необходимо скрыть источник?'               
            }
            
            \$.messager.confirm('Внимание', mes_sr, function(r){
                    if (r){
                             \$.ajax({            
                             type: 'GET',
                             traditional: true,
                             url: 'hide_source.cgi?SID=$SID',
                             data: {'id_sr':row_sr.ID},
                             success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result) {\$('#dg_source_about_us').datagrid('reload');}},
                             error: function() {alert("did not work");}
                             });
                     
                          }   
                  });
        }  
        </script>
		
		<script>
        var url_person;
        function new_person_get_Zayav(){
            \$('#dlg_new_person_get_zayav').dialog('open').dialog('center').dialog('setTitle','Новый пользователь');
            \$('#fm_person_get_zayav').form('clear');
            url_person = 'insert_new_person_get_zayav.cgi?SID=$SID';            
        }
        
        function edit_person_get_Zayav(){
            var row_pers = \$('#dg_who_get_zayav').datagrid('getSelected');
            if (row_pers){
	    \$('#fm_person_get_zayav').form('clear');
	    \$('#dlg_new_person_get_zayav').dialog('open').dialog('center').dialog('setTitle','Редактирование пользователя');
            \$('#fm_person_get_zayav').form('load',row_pers);               
            url_person = 'edit_person_get_zayav.cgi?id_pers='+row_pers.ID+'&SID=$SID';             
            }
        }
        
        function save_person_get_Zayav() {
        var msg   = \$('#fm_person_get_zayav').serialize();
        \$.ajax({
          type: 'GET',
          url: url_person,
          data: msg,
          success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result=="Пользователь добавлен успешно!") {\$('#fm_person_get_zayav').form('clear'); \$('#dlg_new_person_get_zayav').dialog('close'); \$('#dg_who_get_zayav').datagrid('reload');}  if (res.result=="Пользователь отредактирован успешно!") {\$('#fm_person_get_zayav').form('clear'); \$('#dlg_new_person_get_zayav').dialog('close'); \$('#dg_who_get_zayav').datagrid('reload');} }, 
          error: function() {alert("did not work");}        
        });
           
       }
                
       </script>
       
       <script>
       function hide_person_get_Zayav(){
            var row_per = \$('#dg_who_get_zayav').datagrid('getSelected');
            var mes_per;
            if (row_per.FIRED==1)
            {
               mes_per='Вы уверены, что необходимо сделать доступным пользователя?';               
            }
            else
            {
               mes_per='Вы уверены, что необходимо скрыть пользователя?'               
            }
            
            \$.messager.confirm('Внимание', mes_per, function(r){
                    if (r){
                             \$.ajax({            
                             type: 'GET',
                             traditional: true,
                             url: 'hide_person_get_zayav.cgi?SID=$SID',
                             data: {'id_per':row_per.ID},
                             success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result) {\$('#dg_who_get_zayav').datagrid('reload');}},
                             error: function() {alert("did not work");}
                             });
                     
                          }   
                  });
        }  
        </script>
		
		<script>
        var url_course;
        function newCourse(){
            \$('#dlg_course').dialog('open').dialog('center').dialog('setTitle','Новый курс/язык');
            \$('#fm_course').form('clear');
            url_course = 'insert_course.cgi?SID=$SID';            
        }
        
        function editCourse(){
            var row_crs = \$('#dg_course').datagrid('getSelected');
            if (row_crs){
	    \$('#fm_course').form('clear');
	    \$('#dlg_course').dialog('open').dialog('center').dialog('setTitle','Редактирование курса/языка');
            \$('#fm_course').form('load',row_crs);               
            url_course = 'edit_course.cgi?id_crs='+row_crs.ID+'&SID=$SID';             
            }
        }
        
        function saveCourse() {
        var msg   = \$('#fm_course').serialize();
        \$.ajax({
          type: 'GET',
          url: url_course,
          data: msg,
          success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result=="Курс добавлен успешно!") {\$('#fm_course').form('clear'); \$('#dlg_course').dialog('close'); \$('#dg_course').datagrid('reload');}  if (res.result=="Курс отредактирован успешно!") {\$('#fm_course').form('clear'); \$('#dlg_course').dialog('close'); \$('#dg_course').datagrid('reload');} }, 
          error: function() {alert("did not work");}        
        });
           
       }
                
       </script>
       
       <script>
       function hideCourse(){
            var row_cr = \$('#dg_course').datagrid('getSelected');
            var mes_cr;
            if (row_cr.BLOCKED==1)
            {
               mes_cr='Вы уверены, что необходимо сделать доступным курс/язык?';               
            }
            else
            {
               mes_cr='Вы уверены, что необходимо скрыть курс/язык?'               
            }
            
            \$.messager.confirm('Внимание', mes_cr, function(r){
                    if (r){
                             \$.ajax({            
                             type: 'GET',
                             traditional: true,
                             url: 'hide_course.cgi?SID=$SID',
                             data: {'id_cr':row_cr.ID},
                             success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result) {\$('#dg_course').datagrid('reload');}},
                             error: function() {alert("did not work");}
                             });
                     
                          }   
                  });
        }  
        </script>
		
		<script>
        var url_level;
        function newLevel(){
            \$('#dlg_level_lang').dialog('open').dialog('center').dialog('setTitle','Новый уровень владения');
            \$('#fm_level_lang').form('clear');
            url_level = 'insert_level_lang.cgi?SID=$SID';            
        }
        
        function editLevel(){
            var row_lev = \$('#dg_level_lang').datagrid('getSelected');
            if (row_lev){
	    \$('#fm_level_lang').form('clear');
	    \$('#dlg_level_lang').dialog('open').dialog('center').dialog('setTitle','Редактирование уровня владения');
            \$('#fm_level_lang').form('load',row_lev);               
            url_level = 'edit_level_lang.cgi?id_lev='+row_lev.ID+'&SID=$SID';             
            }
        }
        
        function saveLevel() {
        var msg   = \$('#fm_level_lang').serialize();
        \$.ajax({
          type: 'GET',
          url: url_level,
          data: msg,
          success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result=="Уровень владения добавлен успешно!") {\$('#fm_level_lang').form('clear'); \$('#dlg_level_lang').dialog('close'); \$('#dg_level_lang').datagrid('reload');}  if (res.result=="Уровень владения отредактирован успешно!") {\$('#fm_level_lang').form('clear'); \$('#dlg_level_lang').dialog('close'); \$('#dg_level_lang').datagrid('reload');} }, 
          error: function() {alert("did not work");}        
        });
           
       }
                
       </script>
       
       <script>
       function hideLevel(){
            var row_lv = \$('#dg_level_lang').datagrid('getSelected');
            var mes_lv;
            if (row_lv.BLOCKED==1)
            {
               mes_lv='Вы уверены, что необходимо сделать доступным уровень владения?';               
            }
            else
            {
               mes_lv='Вы уверены, что необходимо скрыть уровень владения?'               
            }
            
            \$.messager.confirm('Внимание', mes_lv, function(r){
                    if (r){
                             \$.ajax({            
                             type: 'GET',
                             traditional: true,
                             url: 'hide_level.cgi?SID=$SID',
                             data: {'id_lv':row_lv.ID},
                             success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result) {\$('#dg_level_lang').datagrid('reload');}},
                             error: function() {alert("did not work");}
                             });
                     
                          }   
                  });
        }  
        </script>
		
		<script>
        var url_source_zayav;
        function newSource_Zayav(){
            \$('#dlg_source_zayav').dialog('open').dialog('center').dialog('setTitle','Новый источник заявки');
            \$('#fm_source_zayav').form('clear');
            url_source_zayav = 'insert_source_zayav.cgi?SID=$SID';            
        }
        
        function editSource_Zayav(){
            var row_sr_zv = \$('#dg_source_zayav').datagrid('getSelected');
            if (row_sr_zv){
	    \$('#fm_source_zayav').form('clear');
	    \$('#dlg_source_zayav').dialog('open').dialog('center').dialog('setTitle','Редактирование источника заявки');
            \$('#fm_source_zayav').form('load',row_sr_zv);               
            url_source_zayav = 'edit_source_zayav.cgi?id_srzv='+row_sr_zv.ID+'&SID=$SID';             
            }
        }
        
        function saveSource_Zayav() {
        var msg   = \$('#fm_source_zayav').serialize();
        \$.ajax({
          type: 'GET',
          url: url_source_zayav,
          data: msg,
          success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result=="Источник заявки добавлен успешно!") {\$('#fm_source_zayav').form('clear'); \$('#dlg_source_zayav').dialog('close'); \$('#dg_source_zayav').datagrid('reload');}  if (res.result=="Источник заявки отредактирован успешно!") {\$('#fm_source_zayav').form('clear'); \$('#dlg_source_zayav').dialog('close'); \$('#dg_source_zayav').datagrid('reload');} }, 
          error: function() {alert("did not work");}        
        });
           
       }
                
       </script>
       
       <script>
       function hideSource_Zayav(){
            var row_src_zv = \$('#dg_source_zayav').datagrid('getSelected');
            var mes_src_zv;
            if (row_src_zv.BLOCKED==1)
            {
               mes_src_zv='Вы уверены, что необходимо сделать доступным источник?';               
            }
            else
            {
               mes_src_zv='Вы уверены, что необходимо скрыть источник?'               
            }
            
            \$.messager.confirm('Внимание', mes_src_zv, function(r){
                    if (r){
                             \$.ajax({            
                             type: 'GET',
                             traditional: true,
                             url: 'hide_source_zayav.cgi?SID=$SID',
                             data: {'id_src':row_src_zv.ID},
                             success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result) {\$('#dg_source_zayav').datagrid('reload');}},
                             error: function() {alert("did not work");}
                             });
                     
                          }   
                  });
        }  
        </script>
		
		<script>
        var url_prog;
        function newProg(){
            \$('#dlg_prog').dialog('open').dialog('center').dialog('setTitle','Новая программа обучения');
            \$('#fm_prog').form('clear');
            url_prog = 'insert_prog.cgi?SID=$SID';            
        }
        
        function editProg(){
            var row_prog = \$('#dg_prog').datagrid('getSelected');
            if (row_prog){
	    \$('#fm_prog').form('clear');
	    \$('#dlg_prog').dialog('open').dialog('center').dialog('setTitle','Редактирование программы обучения');
            \$('#fm_prog').form('load',row_prog);               
            url_prog = 'edit_prog.cgi?id_pr='+row_prog.ID+'&SID=$SID';             
            }
        }
        
        function saveProg() {
        var msg   = \$('#fm_prog').serialize();
        \$.ajax({
          type: 'GET',
          url: url_prog,
          data: msg,
          success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result=="Программа добавлена успешно!") {\$('#fm_prog').form('clear'); \$('#dlg_prog').dialog('close'); \$('#dg_prog').datagrid('reload');}  if (res.result=="Программа отредактирована успешно!") {\$('#fm_prog').form('clear'); \$('#dlg_prog').dialog('close'); \$('#dg_prog').datagrid('reload');} }, 
          error: function() {alert("did not work");}        
        });
           
       }
                
       </script>
       
       <script>
       function hideProg(){
            var row_pr = \$('#dg_prog').datagrid('getSelected');
            var mes_pr;
            if (row_pr.BLOCKED==1)
            {
               mes_pr='Вы уверены, что необходимо сделать доступной программу?';               
            }
            else
            {
               mes_pr='Вы уверены, что необходимо скрыть программу?'               
            }
            
            \$.messager.confirm('Внимание', mes_pr, function(r){
                    if (r){
                             \$.ajax({            
                             type: 'GET',
                             traditional: true,
                             url: 'hide_prog.cgi?SID=$SID',
                             data: {'id_prog':row_pr.ID},
                             success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result) {\$('#dg_prog').datagrid('reload');}},
                             error: function() {alert("did not work");}
                             });
                     
                          }   
                  });
        }  
        </script>
		
	    <script>
        var url_type_group;
        function newType_group(){
            \$('#dlg_type_group').dialog('open').dialog('center').dialog('setTitle','Новый тип группы');
            \$('#fm_type_group').form('clear');
            url_type_group = 'insert_type_group.cgi?SID=$SID';            
        }
        
        function editType_group(){
            var row_type_group = \$('#dg_type_group').datagrid('getSelected');
            if (row_type_group){
	    \$('#fm_type_group').form('clear');
	    \$('#dlg_type_group').dialog('open').dialog('center').dialog('setTitle','Редактирование типа группы');
            \$('#fm_type_group').form('load',row_type_group);               
            url_type_group = 'edit_type_group.cgi?id_tp_gr='+row_type_group.ID+'&SID=$SID';             
            }
        }
        
        function saveType_group() {
        var msg   = \$('#fm_type_group').serialize();
        \$.ajax({
          type: 'GET',
          url: url_type_group,
          data: msg,
          success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result=="Тип группы добавлен успешно!") {\$('#fm_type_group').form('clear'); \$('#dlg_type_group').dialog('close'); \$('#dg_type_group').datagrid('reload');}  if (res.result=="Тип группы отредактирован успешно!") {\$('#fm_type_group').form('clear'); \$('#dlg_type_group').dialog('close'); \$('#dg_type_group').datagrid('reload');} }, 
          error: function() {alert("did not work");}        
        });
           
       }
                
       </script>
       
       <script>
       function hideType_group(){
            var row_gr = \$('#dg_type_group').datagrid('getSelected');
            var mes_gr;
            if (row_gr.BLOCKED==1)
            {
               mes_gr='Вы уверены, что необходимо сделать доступным тип группы?';               
            }
            else
            {
               mes_gr='Вы уверены, что необходимо скрыть тип группы?'               
            }
            
            \$.messager.confirm('Внимание', mes_gr, function(r){
                    if (r){
                             \$.ajax({            
                             type: 'GET',
                             traditional: true,
                             url: 'hide_type_group.cgi?SID=$SID',
                             data: {'id_gr':row_gr.ID},
                             success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result) {\$('#dg_type_group').datagrid('reload');}},
                             error: function() {alert("did not work");}
                             });
                     
                          }   
                  });
        }  
        </script>
		
		<script>
        function save_sms_gate() {
        var msg   = \$('#fm_sms_gate').serialize();
        \$.ajax({
          type: 'POST',
          url: 'save_sms_gate.cgi',
          data: msg,
          success: function(res) {\$.messager.alert('Информация',res.result,'info'); }, 
          error: function() {alert("did not work");}        
        });
           
        }
        </script>
        
       <script> //Загрузка данных о СМС шлюзе и вывод их в поля
       \$(function(){
         \$.ajax({            
         type: 'GET',
         traditional: true,
         url: 'get_sms_gate.cgi?SID=$SID',
         success: function(res) {
                                  \$('#SMS_GATE_LOGIN').textbox('setText', res.login);
                                  \$('#SMS_GATE_PSW').textbox('setText', res.psw);                                                                    
                                },
         error: function() {
                             \$('#SMS_GATE_LOGIN').textbox('setText', '');
                             \$('#SMS_GATE_PSW').textbox('setText' ,'');                                                                                 
                           }        
         
                }); 
    
    
        });
        </script>
		
	    <script>
        function hideTeacher(){
            var row_teacher = \$('#dg_teachers').datagrid('getSelected');
            var mes_teacher;
            if (row_teacher.BLOCKED==1)
            {
               mes_teacher='Вы уверены, что необходимо сделать доступным преподавателя?';               
            }
            else
            {
               mes_teacher='Вы уверены, что необходимо скрыть преподавателя?'               
            }
            
            \$.messager.confirm('Внимание', mes_teacher, function(r){
                    if (r){
                             \$.ajax({            
                             type: 'GET',
                             traditional: true,
                             url: 'hide_teacher.cgi?SID=$SID',
                             data: {'id_teacher':row_teacher.ID},
                             success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result) {\$('#dg_teachers').datagrid('reload');}},
                             error: function() {alert("did not work");}
                             });
                     
                          }   
                  });
        }  
        </script>
		
		<script>
        function doClose_Period(){
            \$.messager.confirm('Внимание','Вы уверены, что необходимо закрыть академический год для выбранных групп?',function(r){
                    if (r){
            var ss = [];
            var rows_gr = \$('#dg_groups_4_close_period').datagrid('getSelections');
            for(var i=0; i<rows_gr.length; i++){
                var row = rows_gr[i];
                ss.push(row.ID);
            }
            
             startLoadingAnimation();
            
            \$.ajax({            
            type: 'GET',
            traditional: true,
            url: 'close_period_4_groups.cgi?SID=$SID',
            data: {'dat':ss},
            success: function(res) {\$.messager.alert('Информация',res.result); if (res.result) {\$('#dg_groups_4_close_period').datagrid('reload'); stopLoadingAnimation();}},
            error: function() {alert("did not work"); stopLoadingAnimation();}
            });                 
                         
                         }
                     });
        }
        
        </script>
        
        <script> //Вывод кол-ва выделенных групп
        \$(function(){
        \$('#dg_groups_4_close_period').datagrid({
        onSelect:function(index){
                                 var rows = \$('#dg_groups_4_close_period').datagrid('getSelections');
                                 \$('#lb_gr').text('Кол-во выбранных групп:'+rows.length);        
                                },
        onUnselect:function(index){
                                 var rows = \$('#dg_groups_4_close_period').datagrid('getSelections');
                                 \$('#lb_gr').text('Кол-во выбранных групп:'+rows.length);        
                                },
        onSelectAll:function(index){
                                 var rows = \$('#dg_groups_4_close_period').datagrid('getSelections');
                                 \$('#lb_gr').text('Кол-во выбранных групп:'+rows.length);        
                                },
        onUnselectAll:function(index){
                                 var rows = \$('#dg_groups_4_close_period').datagrid('getSelections');
                                 \$('#lb_gr').text('Кол-во выбранных групп:'+rows.length);        
                                }
                        });
                });
        </script>
        
        <script>
        function startLoadingAnimation() // - функция запуска анимации
        {
          // найдем элемент с изображением загрузки и уберем невидимость:
          var imgObj = \$('#loadImg');
          imgObj.show();
 
          // вычислим в какие координаты нужно поместить изображение загрузки,
          // чтобы оно оказалось в серидине страницы:
          var centerY = \$(window).scrollTop() + (\$(window).height() + imgObj.height())/2;
          var centerX = \$(window).scrollLeft() + (\$(window).width() + imgObj.width())/2;
 
          // поменяем координаты изображения на нужные:
          imgObj.offset({top:centerY, left:centerX});
        }
 
        function stopLoadingAnimation() // - функция останавливающая анимацию
        {
           \$('#loadImg').hide();
        }        
        </script>
		
	   //Отображение контекстной менюхи
       <script>
       \$(function(){
           \$('#dg_groups_4_close_period').datagrid('getPanel').panel('panel').attr('tabindex',0).bind('contextmenu',function(e){
               e.preventDefault();
               \$('#content_group').menu('show', {
                   left: e.pageX,
                   top: e.pageY
               });
           });
       });
       </script>
       /////////////////////////////////
       
       <script>
       function show_content_group(){
            var row_group = \$('#dg_groups_4_close_period').datagrid('getSelected');        
            if (row_group){
            \$('#dlg_student_in_group').window('open').dialog('center').dialog('setTitle','Студенты группы');
            \$('#dg_students_in_group').datagrid({url: 'get_content_group.cgi?SID=$SID&id_group='+row_group.ID});
            }
        }  
        </script>
		
		<script>
        var url_event;
        function newEvent(){
            \$('#dlg_event').dialog('open').dialog('center').dialog('setTitle','Новое мероприятие');
            \$('#fm_event').form('clear');
            url_event = 'insert_event.cgi?SID=$SID';            
        }
        
        function editEvent(){
            var row_event = \$('#dg_events').datagrid('getSelected');
            if (row_event){
	    \$('#fm_event').form('clear');
	    \$('#dlg_event').dialog('open').dialog('center').dialog('setTitle','Редактирование мероприятия');
            \$('#fm_event').form('load',row_event);               
            url_event = 'edit_event.cgi?id_event='+row_event.ID+'&SID=$SID';             
            }
        }
        
        function saveEvent() {
        var msg   = \$('#fm_event').serialize();
        \$.ajax({
          type: 'GET',
          url: url_event,
          data: msg,
          success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result=="Мероприятие добавлено успешно!") {\$('#fm_event').form('clear'); \$('#dlg_event').dialog('close'); \$('#dg_events').datagrid('reload');}  if (res.result=="Мероприятие отредактировано успешно!") {\$('#fm_event').form('clear'); \$('#dlg_event').dialog('close'); \$('#dg_events').datagrid('reload');} }, 
          error: function() {alert("did not work");}        
        });
           
       }
                
       </script>
       
       <script>
       function hideEvent(){
            var row_event = \$('#dg_events').datagrid('getSelected');
            var mes_event;
            if (row_event.BLOCKED==1)
            {
               mes_event='Вы уверены, что необходимо сделать доступным мероприятие?';               
            }
            else
            {
               mes_event='Вы уверены, что необходимо скрыть мероприятие?'               
            }
            
            \$.messager.confirm('Внимание', mes_event, function(r){
                    if (r){
                             \$.ajax({            
                             type: 'GET',
                             traditional: true,
                             url: 'hide_event.cgi?SID=$SID',
                             data: {'id_event':row_event.ID},
                             success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result) {\$('#dg_events').datagrid('reload');}},
                             error: function() {alert("did not work");}
                             });
                     
                          }   
                  });
        }  
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
        <!--<div data-options="region:'east',split:true,title:'Подробности'" style="width:30%;padding:1px;"></div> -->
        <!-- Конец Правый DIV раздел подробности -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->

        <!-- Центральный DIV -рабочая область -->
        <div data-options="region:'center',title:'Рабочая область - Настройки. Пользователь: $formLogin'">

        <!-- Компонент Accordion в котором будут размещаться все разделы -->        
        <div id="acc" class="easyui-accordion" style="width:auto;height:100%">
        
        <div title="Работа с пользователями" style="overflow:auto; padding:10px;">
        
           <!-- Внутрненний layout для представления списка студентов и списка прав по ним --> 
           <div class="easyui-layout" style="width:100%;height:100%;">
             
             <!-- Субправый DIV раздел подробности -->
             <div data-options="region:'east',split:true" title="Подробности" style="width:30%;">
                <table id="pg" style="width:100%"></table>
             </div>
             <!-- Конец Субправый DIV раздел подробности -->
             
             <!-- Субцентральный DIV -рабочая область -->
             <div data-options="region:'center'">
              
                <table id="dg" title="Пользователи" class="easyui-datagrid" style="width:100%;height:100%"
                method="get"
                url="get_users.cgi?SID=$SID"
                toolbar="#tb, #toolbar"
                rownumbers="true" fitColumns="true" singleSelect="true" pagination="true" sortName="FULL_NAME" sortOrder="asc" pageSize="50">

                <thead>
                <tr> 
                  <th field="ID" width="1" hidden="true">ID</th>
                  <th field="LOGIN" width="25" sortable="true">Логин</th>
                  <th field="FULL_NAME" width="157" sortable="true">Полное имя</th>
                  <th field="ADM" width="30" formatter="formatAdm">Администратор</th>
                  <th field="ACTIVE" width="30" formatter="formatStatus">Статус</th>                  
                </tr>
                </thead>
                </table>
                <div id="toolbar">
                    <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="newUser()">Добавить</a>
                    <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="editUser()">Редактировать</a>
                    <a href="#" class="easyui-linkbutton" iconCls="icon-lock" plain="true" onclick="activate_lock()">Заблокировать/Разблокировать</a>
                    <a href="#" class="easyui-linkbutton" iconCls="icon-document" plain="true" onclick=" open_window_change_user_psw()">Сменить пароль</a>
                </div>
                
                <!-- Панель посика -->
                <div id="tb" style="padding:3px">
                <span>Поиск по логину:</span>
                <input id="login" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
                <span>Поиск по полному имени:</span>
                <input id="full_name" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
                <a href="#" class="easyui-linkbutton" plain="false" onclick="doSearch()" style="border-radius:5px; width:100px;">Искать</a>
                </div>
                <!-- Конец Панель для поиска -->              
              
             </div>
             <!-- Конец Субцентральный DIV -рабочая область -->
             
           </div>
           <!-- Конец Внутрненний layout для представления списка студентов и списка прав по ним --> 
            
                
        </div>
        
        <div title="Работа с филиалами" style="overflow:auto;padding:10px;">
		
		<!-- Внутрненний layout для представления списка филиалов --> 
           <div class="easyui-layout" style="width:100%;height:100%;">
             
             <!-- Субправый DIV раздел подробности -->
             <!-- <div data-options="region:'east',split:true" title="Подробности" style="width:30%;"> -->
             <!-- </div> -->
             <!-- Конец Субправый DIV раздел подробности -->
             
             <!-- Субцентральный DIV -рабочая область -->
             <div data-options="region:'center'">
              
                <table id="dg_branches" title="Филиалы" class="easyui-datagrid" style="width:100%;height:100%"
                method="get"
                url="get_branches_adm.cgi?SID=$SID"
                toolbar="#tb_branches, #toolbar_branches"
                rownumbers="true" fitColumns="true" singleSelect="true" pagination="true" sortName="BRANCH" sortOrder="asc" pageSize="50">

                <thead>
                <tr> 
                  <th field="ID" width="1" hidden="true">ID</th>
                  <th field="BRANCH" width="200" sortable="true">Филиал</th>
                  <th field="BLOCKED" width="100" formatter="format_branch">Статус</th>				  
                </tr>
                </thead>
                </table>
                <div id="toolbar_branches">
                    <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="newBranch()">Добавить</a>
                    <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="editBranch()">Редактировать</a>
                    <a href="#" class="easyui-linkbutton" iconCls="icon-lock" plain="true" onclick="hideBranch()">Скрыть/Показать</a>                    
                </div>
                
                <!-- Панель посика -->
                <div id="tb_branches" style="padding:3px">
                <span>Поиск по наименованию:</span>
                <input id="branch_name" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
                <a href="#" class="easyui-linkbutton" plain="false" onclick="doSearch_branch()" style="border-radius:5px; width:100px;">Искать</a>
                </div>
                <!-- Конец Панель для поиска -->              
              
             </div>
             <!-- Конец Субцентральный DIV -рабочая область -->
             
           </div>
           <!-- Конец Внутрненний layout для представления списка филиалов --> 
		
        </div>
        
        <div title="Работа с справочниками" style="overflow:auto;padding:10px;">
		
		<!-- Внутрненний layout для представления списка справочников --> 
           <div class="easyui-layout" style="width:100%;height:100%;">
             
             <!-- Субправый DIV раздел подробности -->
             <!-- <div data-options="region:'east',split:true" title="Подробности" style="width:30%;"> -->
             <!-- </div> -->
             <!-- Конец Субправый DIV раздел подробности -->
             
             <!-- Субцентральный DIV -рабочая область -->
             <div data-options="region:'center'">
             
               <!-- Список табов для отображения справочников --> 
               <div id="tabs_spr" class="easyui-tabs" data-options="pill:true, justified:true" style="width:100%;height:100%">
                   
                   <div title="Источник информации о центре" style="padding:10px">
                   
                      <table id="dg_source_about_us" title="Источник информации" class="easyui-datagrid" style="width:100%;height:100%"
                      method="get"
                      url="get_source_about_us_adm.cgi?SID=$SID"
                      toolbar="#tb_source_about_us, #toolbar_source_about_us"
                      rownumbers="true" fitColumns="true" singleSelect="true" pagination="true" sortName="SOURCE" sortOrder="asc" pageSize="50">

                     <thead>
                     <tr> 
                       <th field="ID" width="1" hidden="true">ID</th>
                       <th field="SOURCE" width="200" sortable="true">Источник</th>
                       <th field="BLOCKED" width="100" formatter="format_source">Статус</th>
                     </tr>
                     </thead>
                     </table>
                     <div id="toolbar_source_about_us">
                       <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="newSource()">Добавить</a>
                       <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="editSource()">Редактировать</a>
                       <a href="#" class="easyui-linkbutton" iconCls="icon-lock" plain="true" onclick="hideSource()">Скрыть/Показать</a>                    
                     </div>
                
                    <!-- Панель посика -->
                    <div id="tb_source_about_us" style="padding:3px">
                    <span>Поиск по источнику:</span>
                    <input id="source_name" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
                    <a href="#" class="easyui-linkbutton" plain="false" onclick="doSearch_source()" style="border-radius:5px; width:100px;">Искать</a>
                    </div>
                    <!-- Конец Панель для поиска -->
                   
                   </div>
                   
                   <div title="Принимающий заявку" style="padding:10px">
				   
				      <table id="dg_who_get_zayav" title="Кто может принимать заявку" class="easyui-datagrid" style="width:100%;height:100%"
                      method="get"
                      url="get_zayav_adm.cgi?SID=$SID"
                      toolbar="#tb_who_get_zayav, #toolbar_who_get_zayav"
                      rownumbers="true" fitColumns="true" singleSelect="true" pagination="true" sortName="FIO" sortOrder="asc" pageSize="50">

                     <thead>
                     <tr> 
                       <th field="ID" width="1" hidden="true">ID</th>
                       <th field="FIO" width="200" sortable="true">ФИО</th>
                       <th field="FIRED" width="100" formatter="format_who_get_zayav">Статус</th>
                     </tr>
                     </thead>
                     </table>
                     <div id="toolbar_who_get_zayav">
                       <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="new_person_get_Zayav()">Добавить</a>
                       <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="edit_person_get_Zayav()">Редактировать</a>
                       <a href="#" class="easyui-linkbutton" iconCls="icon-lock" plain="true" onclick="hide_person_get_Zayav()">Скрыть/Показать</a>                    
                     </div>
                
                    <!-- Панель посика -->
                    <div id="tb_who_get_zayav" style="padding:3px">
                    <span>Поиск по ФИО:</span>
                    <input id="usr_name" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
                    <a href="#" class="easyui-linkbutton" plain="false" onclick="doSearch_source()" style="border-radius:5px; width:100px;">Искать</a>
                    </div>
                    <!-- Конец Панель для поиска -->
				   
                   </div>
                
                   <div title="Курс" style="padding:10px">
				   
				    <table id="dg_course" title="Курс/язык" class="easyui-datagrid" style="width:100%;height:100%"
                    method="get"
                    url="get_course_adm.cgi?SID=$SID"
                    toolbar="#tb_course, #toolbar_course"
                    rownumbers="true" fitColumns="true" singleSelect="true" pagination="true" sortName="LANGUAGE" sortOrder="asc" pageSize="50">

                    <thead>
                    <tr> 
                       <th field="ID" width="1" hidden="true">ID</th>
                       <th field="LANGUAGE" width="200" sortable="true">Наименование курса/языка</th>
                       <th field="BLOCKED" width="100" formatter="format_course">Статус</th>
                    </tr>
                    </thead>
                    </table>
                    <div id="toolbar_course">
                       <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="newCourse()">Добавить</a>
                       <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="editCourse()">Редактировать</a>
                       <a href="#" class="easyui-linkbutton" iconCls="icon-lock" plain="true" onclick="hideCourse()">Скрыть/Показать</a>
                    </div>
                
                    <!-- Панель посика -->
                    <div id="tb_course" style="padding:3px">
                    <span>Поиск по курсу/языку:</span>
                    <input id="course_name" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
                    <a href="#" class="easyui-linkbutton" plain="false" onclick="doSearch_course()" style="border-radius:5px; width:100px;">Искать</a>
                    </div>
                    <!-- Конец Панель для поиска -->
				   
                   </div>
                   
                   <div title="Уровень владения языком" style="padding:10px">
				   
				      <table id="dg_level_lang" title="Уровень языка" class="easyui-datagrid" style="width:100%;height:100%"
                      method="get"
                      url="get_level_lang_adm.cgi?SID=$SID"
                      toolbar="#tb_level_lang, #toolbar_level_lang"
                      rownumbers="true" fitColumns="true" singleSelect="true" pagination="true" sortName="LEVEL" sortOrder="asc" pageSize="50">

                     <thead>
                     <tr> 
                       <th field="ID" width="1" hidden="true">ID</th>
                       <th field="LEVEL" width="200" sortable="true">Уровень владения</th>
                       <th field="BLOCKED" width="100" formatter="format_level_lang">Статус</th>
                     </tr>
                     </thead>
                     </table>
                     <div id="toolbar_level_lang">
                       <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="newLevel()">Добавить</a>
                       <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="editLevel()">Редактировать</a>
                       <a href="#" class="easyui-linkbutton" iconCls="icon-lock" plain="true" onclick="hideLevel()">Скрыть/Показать</a>
                     </div>
                
                    <!-- Панель посика -->
                    <div id="tb_level_lang" style="padding:3px">
                    <span>Поиск по уровню владения:</span>
                    <input id="level_lang_name" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
                    <a href="#" class="easyui-linkbutton" plain="false" onclick="doSearch_level_lang()" style="border-radius:5px; width:100px;">Искать</a>
                    </div>
                    <!-- Конец Панель для поиска -->
				   
                   </div>
                
                   <div title="Источник заявки" style="padding:10px">
				   
				      <table id="dg_source_zayav" title="Источник заявки" class="easyui-datagrid" style="width:100%;height:100%"
                      method="get"
                      url="get_source_zayav_adm.cgi?SID=$SID"
                      toolbar="#tb_source_zayav, #toolbar_source_zayav"
                      rownumbers="true" fitColumns="true" singleSelect="true" pagination="true" sortName="SOURCE" sortOrder="asc" pageSize="50">

                     <thead>
                     <tr> 
                       <th field="ID" width="1" hidden="true">ID</th>
                       <th field="SOURCE" width="200" sortable="true">Источник</th>
                       <th field="BLOCKED" width="100" formatter="format_source_zayav">Статус</th>
                     </tr>
                     </thead>
                     </table>
                     <div id="toolbar_source_zayav">
                       <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="newSource_Zayav()">Добавить</a>
                       <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="editSource_Zayav()">Редактировать</a>
                       <a href="#" class="easyui-linkbutton" iconCls="icon-lock" plain="true" onclick="hideSource_Zayav()">Скрыть/Показать</a>
                     </div>
                
                    <!-- Панель посика -->
                    <div id="tb_source_zayav" style="padding:3px">
                    <span>Поиск по источнику:</span>
                    <input id="source_zayav_name" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
                    <a href="#" class="easyui-linkbutton" plain="false" onclick="doSearch_source_zayav()" style="border-radius:5px; width:100px;">Искать</a>
                    </div>
                    <!-- Конец Панель для поиска -->
				   
                   </div>
                   
                   <div title="Программа" style="padding:10px">
				   
				     <table id="dg_prog" title="Программа обучения" class="easyui-datagrid" style="width:100%;height:100%"
                     method="get"
                     url="get_prog_adm.cgi?SID=$SID"
                     toolbar="#tb_prog, #toolbar_prog"
                     rownumbers="true" fitColumns="true" singleSelect="true" sortName="groupField" sortOrder="asc" data-options="view:groupview, groupField:'groupField', groupFormatter:function(value,rows){ return value + ' - ' + rows.length; }">

                     <thead>
                     <tr>                        
                       <th field="ID" width="1" hidden="true">ID</th>                       
                       <th field="NAME_PROGRAMM" width="200" sortable="true">Наименование</th>
                       <th field="BLOCKED" width="100" formatter="format_prog">Статус</th>                       
                       <th field="groupField" width="1" hidden="true">gr</th>
                     </tr>
                     </thead>
                     </table>
                     <div id="toolbar_prog">
                       <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="newProg()">Добавить</a>
                       <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="editProg()">Редактировать</a>
                       <a href="#" class="easyui-linkbutton" iconCls="icon-lock" plain="true" onclick="hideProg()">Скрыть/Показать</a>
                     </div>
                
                     <!-- Панель посика -->
                     <div id="tb_prog" style="padding:3px">
                     <span>Поиск по наименованию:</span>
                     <input id="prog_name" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
                     <a href="#" class="easyui-linkbutton" plain="false" onclick="doSearch_prog()" style="border-radius:5px; width:100px;">Искать</a>
                     </div>
                     <!-- Конец Панель для поиска -->
				   
                   </div>
                   
                   <div title="Тип группы" style="padding:10px">
				   
				      <table id="dg_type_group" title="Тип группы" class="easyui-datagrid" style="width:100%;height:100%"
                      method="get"
                      url="get_type_group_adm.cgi?SID=$SID"
                      toolbar="#tb_type_group, #toolbar_type_group"
                      rownumbers="true" fitColumns="true" singleSelect="true" pagination="true" sortName="GROUPS" sortOrder="asc" pageSize="50">

                     <thead>
                     <tr>                        
                       <th field="ID" width="1" hidden="true">ID</th>                       
                       <th field="GROUPS" width="200" sortable="true">Тип группы</th>
                       <th field="PRICE" width="50">Стоимость обучения</th>                       
                       <th field="TYPE_OPL" width="50">Тип оплаты</th>
                       <th field="DURATION" width="100">Длительность занятий</th>
                       <th field="DIRECTION_STUDY" width="100">Направление обучения</th>
                       <th field="BLOCKED" width="100" formatter="format_type_group">Статус</th> 
                     </tr>
                     </thead>
                     </table>
                     <div id="toolbar_type_group">
                       <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="newType_group()">Добавить</a>
                       <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="editType_group()">Редактировать</a>
                       <a href="#" class="easyui-linkbutton" iconCls="icon-lock" plain="true" onclick="hideType_group()">Скрыть/Показать</a>
                     </div>
                
                     <!-- Панель посика -->
                     <div id="tb_type_group" style="padding:3px">
                     <span>Поиск по типу группы:</span>
                     <input id="type_group_name" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
                     <a href="#" class="easyui-linkbutton" plain="false" onclick="doSearch_type_group()" style="border-radius:5px; width:100px;">Искать</a>
                     </div>
                     <!-- Конец Панель для поиска -->
				   
                   </div>
				   
				   <div title="Учителя" style="padding:10px">
                      
                      <table id="dg_teachers" title="Учителя" class="easyui-datagrid" style="width:100%;height:100%"
                      method="get"
                      url="get_teachers_adm.cgi?SID=$SID"
                      toolbar="#tb_teachers, #toolbar_teachers"
                      rownumbers="true" fitColumns="true" singleSelect="true" pagination="true" sortName="FIO" sortOrder="asc" pageSize="50">

                     <thead>
                     <tr>                        
                       <th field="ID" width="1" hidden="true">ID</th>                       
                       <th field="FIO" width="200" sortable="true">ФИО</th>
                       <th field="POSITION" width="50">Должность</th>                       
                       <th field="PHONE" width="50">Телефон</th>
                       <th field="BLOCKED" width="100" formatter="format_teachers">Статус</th> 
                     </tr>
                     </thead>
                     </table>
                     <div id="toolbar_teachers">
                       <a href="#" class="easyui-linkbutton" iconCls="icon-lock" plain="true" onclick="hideTeacher()">Скрыть/Показать</a>
                     </div>
                
                     <!-- Панель посика -->
                     <div id="tb_teachers" style="padding:3px">
                     <span>Поиск по ФИО:</span>
                     <input id="fio_teacher" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
                     <a href="#" class="easyui-linkbutton" plain="false" onclick="doSearch_teacher()" style="border-radius:5px; width:100px;">Искать</a>
                     </div>
                     <!-- Конец Панель для поиска -->
                                      
                   </div>
				   
				   <div title="Мероприятия" style="padding:10px">
                   
                   <table id="dg_events" title="Мероприятия" class="easyui-datagrid" style="width:100%;height:100%"
                      method="get"
                      url="get_events.cgi?SID=$SID"
                      toolbar="#tb_events, #toolbar_events"
                      rownumbers="true" fitColumns="true" singleSelect="true" pagination="true" sortName="NAME_EVENT" sortOrder="asc" pageSize="50">

                     <thead>
                     <tr>                        
                       <th field="ID" width="1" hidden="true">ID</th>                       
                       <th field="NAME_EVENT" width="200" sortable="true">Наименование мероприятия</th>                       
                       <th field="BLOCKED" width="100" formatter="format_type_group">Статус</th> 
                     </tr>
                     </thead>
                     </table>
                     <div id="toolbar_events">
                       <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="newEvent()">Добавить</a>
                       <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="editEvent()">Редактировать</a>
                       <a href="#" class="easyui-linkbutton" iconCls="icon-lock" plain="true" onclick="hideEvent()">Скрыть/Показать</a>
                     </div>
                
                     <!-- Панель посика -->
                     <div id="tb_events" style="padding:3px">
                     <span>Поиск по мероприятию:</span>
                     <input id="event_name" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
                     <a href="#" class="easyui-linkbutton" plain="false" onclick="doSearch_event()" style="border-radius:5px; width:100px;">Искать</a>
                     </div>
                     <!-- Конец Панель для поиска -->
                     
                   </div>  
                
               </div>
               <!-- Конец Список табов для отображения справочников -->
                
             </div>
             <!-- Конец Субцентральный DIV -рабочая область -->
             
           </div>
           <!-- Конец Внутрненний layout для представления списка справочников -->    		
				
        </div>
		
		<div title="Активные сессии пользователей" style="overflow:auto;padding:10px;">
        
        <!-- Внутрненний layout для представления сессий пользователей --> 
           <div class="easyui-layout" style="width:100%;height:100%;">
             
             <!-- Субправый DIV раздел подробности -->
             <!-- <div data-options="region:'east',split:true" title="Подробности" style="width:30%;"> -->
             <!-- </div> -->
             <!-- Конец Субправый DIV раздел подробности -->
             
             <!-- Субцентральный DIV -рабочая область -->
             <div data-options="region:'center'">
              
                <table id="dg_sessions" title="Сессии" class="easyui-datagrid" style="width:100%;height:100%"
                method="get"
                url="get_sessions.cgi?SID=$SID"
                toolbar="#toolbar_sessions"
                rownumbers="true" fitColumns="true" singleSelect="true" pagination="true" sortName="id" sortOrder="asc" pageSize="50">

                <thead>
                <tr> 
                  <th field="id" width="150">ID сессии</th>
                  <th field="a_session" width="100">Логин пользователя</th>
                </tr>
                </thead>
                </table>
                <div id="toolbar_sessions">
                    <a href="#" class="easyui-linkbutton" iconCls="icon-remove" plain="true" onclick="del_session()">Удалить сессию</a>                    
                </div>
              
             </div>
             <!-- Конец Субцентральный DIV -рабочая область -->
             
           </div>
           <!-- Конец Внутрненний layout для представления сессий пользователей -->        
        </div>
		
		<!-- Внутрненний layout для настроек шлюза СМС -->
		<div title="СМС-шлюз" style="overflow:auto;padding:10px;">
             
             <div style="margin-left:10px; margin-top:10px;">
                <span style="font-weight: bold;">Введите логин и пароль SMS - шлюза.</span>
                <br />
                <div style="margin-top:10px;">
                  <form id="fm_sms_gate" novalidate>              
                  <div class="fitem">
                  <label>Логин:</label>
                  <input id="SMS_GATE_LOGIN" name="SMS_GATE_LOGIN" class="easyui-textbox" required missingMessage="Данное поле необходимо заполнить">
	          </div>
	          <div class="fitem">
       	          <label>Пароль</label>
           	  <input id="SMS_GATE_PSW" name="SMS_GATE_PSW" type="password" class="easyui-textbox" required missingMessage="Данное поле необходимо заполнить">
           	  
           	  <input name="SID" id="SID" type="hidden" value="$SID" />
           	  </div>
                  </form>
                </div>   
                </ br>
                <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="save_sms_gate()" style="width:100px">Сохранить</a>             
             </div>
             
        </div>
		<!-- Конец Внутрненний layout для настроек шлюза СМС -->
		
		<!-- Внутрненний layout закрытия текущего академического года -->
        <div title="Закрытие текущего академ. года" style="overflow:auto;padding:10px;">
             
                <span id="lb_gr" style="float:left; font-weight: bold; margin-bottom:10px;">Кол-во выбранных групп:</span>
                <table id="dg_groups_4_close_period" title="Закрытие текущего академического года для выбранных групп" class="easyui-datagrid" style="width:100%;height:87%"
                method="get"
                url="get_groups_4_close_period.cgi?SID=$SID"
                footer:'#ft_close_per'
                rownumbers="true" fitColumns="true" sortName="GROUP_NAME" sortOrder="asc" striped=true>

                <thead>
                <tr> 
                  <th field="ck_bx" checkbox="true"></th>
                  <th field="ID" width="1" hidden="true">ID</th>
                  <th field="GROUP_NAME" width="100" sortable="true">Наименование группы</th>
                  <th field="LANGUAGE" width="100">Язык</th>                  
                  <th field="NAME_PROGRAMM" width="100">Программа</th>                                    
                </tr>
                </thead>
                </table>
                
                <div id="ft_close_per" style="padding:10px; margin-left:45%;">
                <a href="#" class="easyui-linkbutton" plain="false" onclick="doClose_Period();" style="border-radius:5px; width:150px;">Выполнить</a>
                </div>
             
             
        </div> 
        <!-- Конец Внутрненний layout закрытия текущего академического года --> 
        
        
        </div>
        <!-- Конец Компонент Accordion в котором будут размещаться все разделы -->        
        

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
    
   <!-- Форма добавления нового пользователя -->    
    <div id="dlg_new_user" class="easyui-dialog" style="width:515px;height:600px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons_new_user" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Информация о пользователе и его правах</div>
        <form id="fm_user" novalidate>              
         <div class="fitem">
                <label><b>Общая информация.</b></label>
                </div>
         <div class="fitem">
               <label>Логин:</label>
               <input name="LOGIN" class="easyui-textbox" required missingMessage="Данное поле необходимо заполнить">
	        </div>
	 <div class="fitem">
       	        <label>ФИО пользователя:</label>
           	<input name="FULL_NAME" class="easyui-textbox" required missingMessage="Данное поле необходимо заполнить">
           	</div>         
         <div class="fitem">
                <label><b>Статус пользователя.</b></label>
                </div>	 
	 <div class="fitem">
               	<label>Администратор:</label>
               	<input name="ADM" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
                <label><b>Права пользователя.</b></label>
                </div>
	 <div class="fitem">
               	<label><b>Главный раздел-Секретариат:</b></label>
               	<input id="TOP_SEKRETARIAT" name="TOP_SEKRETARIAT" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Главная:</label>
               	<input name="MAIN_SEKRETARIAT" style="height:17px" class="easyui-switchbutton sekretariat" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Группы:</label>
               	<input name="GROUPS_SEKRETARIAT" style="height:17px" class="easyui-switchbutton sekretariat" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Студенты:</label>
               	<input name="STUDENTS_SEKRETARIAT" style="height:17px" class="easyui-switchbutton sekretariat" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Учителя:</label>
               	<input name="TEACHERS_SEKRETARIAT" style="height:17px" class="easyui-switchbutton sekretariat" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Кабинеты:</label>
               	<input name="ROOMS_SEKRETARIAT" style="height:17px" class="easyui-switchbutton sekretariat" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Календарь:</label>
               	<input name="CALENDAR_SEKRETARIAT" style="height:17px" class="easyui-switchbutton sekretariat" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Личный календарь:</label>
               	<input name="PERSONAL_CALENDAR_SEKRETARIAT" style="height:17px" class="easyui-switchbutton sekretariat" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Фирмы:</label>
               	<input name="FIRMS_SEKRETARIAT" style="height:17px" class="easyui-switchbutton sekretariat" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Связь:</label>
               	<input name="LINK_SEKRETARIAT" style="height:17px" class="easyui-switchbutton sekretariat" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>СМС:</label>
               	<input name="SMS_SEKRETARIAT" style="height:17px" class="easyui-switchbutton sekretariat" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Документы:</label>
               	<input name="DOCUMENTS_SEKRETARIAT" style="height:17px" class="easyui-switchbutton sekretariat" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Пользователи:</label>
               	<input name="USERS_SEKRETARIAT" style="height:17px" class="easyui-switchbutton sekretariat" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Заявки:</label>
               	<input name="ZAYAV_SEKRETARIAT" style="height:17px" class="easyui-switchbutton sekretariat" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Резерв:</label>
               	<input name="RESERV_SEKRETARIAT" style="height:17px" class="easyui-switchbutton sekretariat" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Настройки:</label>
               	<input name="OPTIONS_SEKRETARIAT" style="height:17px" class="easyui-switchbutton sekretariat" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label><b>Главный раздел-Финансы:</b></label>
               	<input id="TOP_FINANCE" name="TOP_FINANCE" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Транзакции:</label>
               	<input name="TRANSACTION_FINANCE" style="height:17px" class="easyui-switchbutton finance" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Счет-фактуры:</label>
               	<input name="SCHET_FACTUR_FINANCE" style="height:17px" class="easyui-switchbutton finance" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Приходные ордера:</label>
               	<input name="PRIH_ORDER_FINANCE" style="height:17px" class="easyui-switchbutton finance" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Импорт файлов из банка:</label>
               	<input name="IMPORT_FILES_BANK_FINANCE" style="height:17px" class="easyui-switchbutton finance" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Экспорт файлов в банк:</label>
               	<input name="EXPORT_FILES_BANK_FINANCE" style="height:17px" class="easyui-switchbutton finance" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Настройки:</label>
               	<input name="OPTIONS_FINANCE" style="height:17px" class="easyui-switchbutton finance" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label><b>Главный раздел-Регистрация:</b></label>
               	<input id="TOP_REGISTRATION" name="TOP_REGISTRATION" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Формуляры:</label>
               	<input name="FORMULARS_REGISTRATION" style="height:17px" class="easyui-switchbutton registration" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Настройки:</label>
               	<input name="OPTIONS_REGISTRATIONS" style="height:17px" class="easyui-switchbutton registration" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label><b>Главный раздел-E-learning:</b></label>
               	<input id="TOP_E_LEARNING" name="TOP_E_LEARNING" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Тесты:</label>
               	<input name="TESTS_E_LEARNING" style="height:17px" class="easyui-switchbutton e_learning" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Этикетки:</label>
               	<input name="LABELS_E_LEARNING" style="height:17px" class="easyui-switchbutton e_learning" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Файлы филиалов:</label>
               	<input name="FILES_OF_BRANCH_E_LEARNING" style="height:17px" class="easyui-switchbutton e_learning" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Файлы:</label>
               	<input name="FILES_E_LEARNING" style="height:17px" class="easyui-switchbutton e_learning" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Файлы учителей:</label>
               	<input name="FILES_OF_TEACHERS_E_LEARNING" style="height:17px" class="easyui-switchbutton e_learning" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label><b>Главный раздел-Мультимедиатека:</b></label>
               	<input id="TOP_MULTIMEDIATEKA" name="TOP_MULTIMEDIATEKA" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Список позиций:</label>
               	<input name="LIST_OF_POSITION_MULTIMEDIATEKA" style="height:17px" class="easyui-switchbutton multimediateka" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Настройки:</label>
               	<input name="OPTIONS_MULTIMEDIATEKA" style="height:17px" class="easyui-switchbutton multimediateka" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label><b>Главный раздел-Суперадмин:</b></label>
               	<input id="TOP_SUPERADMIN" name="TOP_SUPERADMIN" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Филиалы:</label>
               	<input name="BRANCHES_SUPERADMIN" style="height:17px" class="easyui-switchbutton superadmin" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Суперадминистраторы:</label>
               	<input name="SUPERADMINISTRATORS_SUPERADMIN" style="height:17px" class="easyui-switchbutton superadmin" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Настройки:</label>
               	<input name="OPTIONS_SUPERADMIN" style="height:17px" class="easyui-switchbutton superadmin" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label><b>Главный раздел-Отчеты:</b></label>
               	<input id="TOP_REPORTS" name="TOP_REPORTS" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Должники на сегодня:</label>
               	<input name="REPORTS_REPORTS" style="height:17px" class="easyui-switchbutton reports" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Должники за месяц:</label>
               	<input name="DEBTS_MONTH_REPORTS" style="height:17px" class="easyui-switchbutton reports" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>План-Факт по филиалам (за период):</label>
               	<input name="PLAN_FACT_REPORTS" style="height:17px" class="easyui-switchbutton reports" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Реальные поступления за месяц по филиалам:</label>
               	<input name="PLAN_FACT_REAL_PAYS_MONTH_REPORTS" style="height:17px" class="easyui-switchbutton reports" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Студенты/Преподаватели:</label>
               	<input name="STUDENTS_TEACHERS_REPORTS" style="height:17px" class="easyui-switchbutton reports" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
     <div class="fitem">
               	<label>Студенты по возрасту:</label>
               	<input name="STUDENTS_AGE_REPORTS" style="height:17px" class="easyui-switchbutton reports" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Студенты/Договоры:</label>
               	<input name="STUDENTS_DOGOVORS" style="height:17px" class="easyui-switchbutton reports" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label><b>Главный раздел-E-журнал:</b></label>
               	<input id="TOP_E_JOURNAL" name="TOP_E_JOURNAL" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label><b>Главный раздел-Контроллер:</b></label>
               	<input id="TOP_CONTROLLER" name="TOP_CONTROLLER" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label><b>Главный раздел-Анкеты:</b></label>
               	<input id="TOP_ANKETS" name="TOP_ANKETS" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Анкеты:</label>
               	<input name="ANKETS_ANKETS" style="height:17px" class="easyui-switchbutton ancets" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Этикетки:</label>
               	<input name="LABELS_ANKETS" style="height:17px" class="easyui-switchbutton ancets" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
                <label><b>Доступ к функциям.</b></label>
                </div>
         <div class="fitem">
               	<label>Удаление договора у студента:</label>
               	<input name="ABLE_DELETE_STUDENT_DOGOVOR" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Удаление заявок:</label>
               	<input name="ABLE_DELETE_ZAYAVKI" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Удаление групп:</label>
               	<input name="ABLE_DELETE_GROUP" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Удаление студентов из группы:</label>
               	<input name="ABLE_DEL_STUDENT_FROM_GROUP" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Удаление занятий/уроков из группы:</label>
               	<input name="ABLE_DEL_LESSONS_FROM_GROUP" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Установка даты начала обучения:</label>
               	<input name="ABLE_SET_BEGIN_STUDY" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Изменение суммы к оплате:</label>
               	<input name="ABLE_CHANGE_SUMM_4_OPL" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
     <div class="fitem">
               	<label>Добавление периода для оплаты:</label>
               	<input name="ABLE_ADD_PERIOD_OF_PAYS" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Удаление периода для оплаты:</label>
               	<input name="ABLE_DEL_PERIOD_OF_PAYS" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
     <div class="fitem">
               	<label>Отправка СМС:</label>
               	<input name="ABLE_SEND_SMS" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
       	        <label>Период действия пароля (дней):</label>
            	<input id="PASSW_DAYS_OF_LIVE" name="PASSW_DAYS_OF_LIVE" class="easyui-numberbox" value="40" style="width:60px;" required missingMessage="Данное поле необходимо заполнить">
           	</div> 
	 <div class="fitem">
               	<label>Добавление мероприятия:</label>
               	<input name="ABLE_ADD_EVENT" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Редактирование мероприятия:</label>
               	<input name="ABLE_EDIT_EVENT" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
	 <div class="fitem">
               	<label>Удаление мероприятия:</label>
               	<input name="ABLE_DEL_EVENT" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>
     <div class="fitem">
               	<label>Перемещение студентов между группами:</label>
               	<input name="ABLE_MOVE_STUDENTS_BETWEEN_GROUPS" style="height:17px" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
	        </div>			
        </form>
    </div>
    <div id="dlg-buttons_new_user">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="saveUser()" style="width:100px">Сохранить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript: \$('#dlg_new_user').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма добавления нового пользователя -->
    
    
    <!-- Форма изменения пароля пользователя -->    
    <div id="dlg_change_psw_user" class="easyui-dialog" style="width:500px;height:200px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons_change_psw_user" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Новый пароль пользователя</div>
        <form id="fm_change_psw_user" novalidate>              
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
    <div id="dlg-buttons_change_psw_user">
        <a href="#" class="easyui-linkbutton" iconCls="icon-more" onclick="get_gen_psw()" style="float:left;">Сгенерировать пароль</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="change_psw_user()" style="width:100px">Ок</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript: \$('#dlg_change_psw_user').dialog('close')" style="width:90px">Отменить</a>        
    </div>
    <!-- Конец Форма изменения пароля пользователя -->
	
	<!-- Форма добавления нового филиала -->    
    <div id="dlg_new_branch" class="easyui-dialog" style="width:500px;height:180px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons_new_branch" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Информация о филиале</div>
        <form id="fm_branch" novalidate>
         <div class="fitem">
               <label>Наименование:</label>
               <input name="BRANCH" class="easyui-textbox" required missingMessage="Данное поле необходимо заполнить">
	        </div>
        </form>
    </div>
    <div id="dlg-buttons_new_branch">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="saveBranch()" style="width:100px">Сохранить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript: \$('#dlg_new_branch').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма добавления нового филиала -->
	
	<!-- Форма добавления нового источника -->    
    <div id="dlg_new_source_about_us" class="easyui-dialog" style="width:500px;height:180px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons_new_source_about_us" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Информация об источнике</div>
        <form id="fm_source_about_us" novalidate>
         <div class="fitem">
               <label>Наименование:</label>
               <input name="SOURCE" class="easyui-textbox" required missingMessage="Данное поле необходимо заполнить">
	        </div>
        </form>
    </div>
    <div id="dlg-buttons_new_source_about_us">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="saveSource()" style="width:100px">Сохранить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript: \$('#dlg_new_source_about_us').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма добавления нового источника -->
	
	<!-- Форма добавления нового пользователя для приема заявки -->    
    <div id="dlg_new_person_get_zayav" class="easyui-dialog" style="width:500px;height:180px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons_new_person_get_zayav" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Информация о пользователе</div>
        <form id="fm_person_get_zayav" novalidate>
         <div class="fitem">
               <label>ФИО:</label>
               <input name="FIO" class="easyui-textbox" required missingMessage="Данное поле необходимо заполнить">
	        </div>
        </form>
    </div>
    <div id="dlg-buttons_new_person_get_zayav">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="save_person_get_Zayav()" style="width:100px">Сохранить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript: \$('#dlg_new_person_get_zayav').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма добавления нового пользователя для приема заявки -->
	
	<!-- Форма добавления нового курса -->    
    <div id="dlg_course" class="easyui-dialog" style="width:500px;height:180px;padding:10px 1px;"
            closed="true" buttons="#dlg-course" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Информация о курсе/языке</div>
        <form id="fm_course" novalidate>
         <div class="fitem">
               <label>Курс/Язык:</label>
               <input name="LANGUAGE" class="easyui-textbox" required missingMessage="Данное поле необходимо заполнить">
	        </div>
        </form>
    </div>
    <div id="dlg-course">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="saveCourse()" style="width:100px">Сохранить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript: \$('#dlg_course').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма добавления нового курса -->
	
	 <!-- Форма добавления нового уровня владения языком -->    
    <div id="dlg_level_lang" class="easyui-dialog" style="width:500px;height:180px;padding:10px 1px;"
            closed="true" buttons="#dlg-level_lang" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Информация об уровне владения языком</div>
        <form id="fm_level_lang" novalidate>
         <div class="fitem">
               <label>Уровень владения:</label>
               <input name="LEVEL" class="easyui-textbox" required missingMessage="Данное поле необходимо заполнить">
	        </div>
        </form>
    </div>
    <div id="dlg-level_lang">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="saveLevel()" style="width:100px">Сохранить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript: \$('#dlg_level_lang').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма добавления нового уровня владения языком -->
	
	<!-- Форма добавления нового источника заявки -->    
    <div id="dlg_source_zayav" class="easyui-dialog" style="width:500px;height:180px;padding:10px 1px;"
            closed="true" buttons="#dlg-source_zayav" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Информация об источнике заявки</div>
        <form id="fm_source_zayav" novalidate>
         <div class="fitem">
               <label>Источник:</label>
               <input name="SOURCE" class="easyui-textbox" required missingMessage="Данное поле необходимо заполнить">
	        </div>
        </form>
    </div>
    <div id="dlg-source_zayav">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="saveSource_Zayav()" style="width:100px">Сохранить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript: \$('#dlg_source_zayav').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма добавления нового источника заявки -->
	
	<!-- Форма добавления новой программы обучения -->    
    <div id="dlg_prog" class="easyui-dialog" style="width:500px;height:210px;padding:10px 1px;"
            closed="true" buttons="#dlg-prog" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Информация о программе</div>
        <form id="fm_prog" novalidate>
         <div class="fitem">
               <label>Наименование:</label>
               <input name="NAME_PROGRAMM" class="easyui-textbox" required missingMessage="Данное поле необходимо заполнить">
	        </div>
	 <div class="fitem">
               	<label>Тип программы:</label>
               	<input name="groupField" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'text', url: 'get_progs_adm.cgi?SID=$SID', method: 'get'" missingMessage="Данное поле необходимо заполнить">
           	</div>
        </form>
    </div>
    <div id="dlg-prog">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="saveProg()" style="width:100px">Сохранить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript: \$('#dlg_prog').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма добавления новой программы обучения -->
	
	<!-- Форма добавления нового типа группы -->    
    <div id="dlg_type_group" class="easyui-dialog" style="width:750px;height:310px;padding:10px 1px;"
            closed="true" buttons="#dlg-type_group" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Информация о типе группы</div>
        <form id="fm_type_group" novalidate>
         <div class="fitem">
               <label>Тип группы:</label>
               <input name="GROUPS" class="easyui-combobox" data-options="required:true, panelHeight:'auto', valueField: 'text', url: 'get_type_gr_adm.cgi?SID=$SID', method: 'get'" missingMessage="Данное поле необходимо заполнить">
	       </div>
	     <div class="fitem">
               	<label>Стоимость обучения:</label>
                <!--	<input name="PRICE" class="easyui-combobox" data-options="required:true, panelHeight:'auto', valueField: 'text', url: 'get_price_adm.cgi?SID=$SID', method: 'get'" missingMessage="Данное поле необходимо заполнить"> -->
				 <input name="PRICE" class="easyui-textbox" data-options="required:true" missingMessage="Данное поле необходимо заполнить">
           	</div>
		 <div class="fitem">
               	<label>Валюта:</label>
               	<input name="CURRENCY" class="easyui-combobox" data-options="required:true, panelHeight:'auto', valueField: 'text', url: 'get_currency.cgi?SID=$SID', method: 'get'" missingMessage="Данное поле необходимо заполнить">
           	</div>
         <div class="fitem">
               	<label>Тип оплаты:</label>
               	<input name="TYPE_OPL" class="easyui-combobox" data-options="required:true, panelHeight:'auto', valueField: 'text', url: 'get_type_opl_adm.cgi?SID=$SID', method: 'get'" missingMessage="Данное поле необходимо заполнить">
           	</div>
         <div class="fitem">
               	<label>Длительность занятий:</label>
               	<input name="DURATION" class="easyui-combobox" data-options="required:true, panelHeight:'auto', valueField: 'text', url: 'get_duration_adm.cgi?SID=$SID', method: 'get'" missingMessage="Данное поле необходимо заполнить">
           	</div>
         <div class="fitem">
               	<label>Направление обучения:</label>
               	<input name="DIRECTION_STUDY" class="easyui-combobox" data-options="panelHeight:'auto', valueField: 'text', url: 'get_direction_study_adm.cgi?SID=$SID', method: 'get'">
               	</div>        
        </form>
    </div>
    <div id="dlg-type_group">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="saveType_group()" style="width:100px">Сохранить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript: \$('#dlg_type_group').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма добавления нового типа группы -->
	
	<!-- Вывод картинки лоадера -->
    <img id="loadImg" src="../images/loader.gif" /> 
    
    <!--Контекстное меню просмотра содержимого группы-->
    <div id="content_group" class="easyui-menu" style="width:300px;">
        <div data-options="iconCls:'icon-tip'" onclick="show_content_group()"><strong>Посмотреть привязанных студентов</strong></div>
    </div>
    <!--Конец Контекстное меню  просмотра содержимого группы-->
    
    <!-- Форма отображения привязанных к группе студентов при закрытии академ года -->    
    <div id="dlg_student_in_group" class="easyui-dialog" style="width:500px;height:450px;padding:10px 5px 0px 5px;"
            closed="true" modal="true" buttons="#dlg-buttons_student_in_group" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <table id="dg_students_in_group" class="easyui-datagrid" style="width:100%;height:95%"
        method="get" fitColumns="true" singleSelect="true" striped=true>

        <thead>
        <tr>            
            <th field="PUPILS_NUM_DOGOVOR" width="80"><b>№договора</b></th>
            <th field="FIO" width="250"><b>ФИО</b></th>                                                
        </tr>
        </thead>
        </table>        
    </div> 
    <div id="dlg-buttons_student_in_group">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_student_in_group').dialog('close')" style="width:90px">Закрыть</a>
    </div>
    <!-- Конец Форма отображения привязанных к группе студентов при закрытии академ года -->
	
	<!-- Форма добавления нового мероприятия -->    
    <div id="dlg_event" class="easyui-dialog" style="width:500px;height:180px;padding:10px 1px;"
            closed="true" buttons="#dlg-event" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Информация о мероприятии</div>
        <form id="fm_event" novalidate>
         <div class="fitem">
               <label>Мероприятие:</label>
               <input name="NAME_EVENT" class="easyui-textbox" required missingMessage="Данное поле необходимо заполнить">
	        </div>
        </form>
    </div>
    <div id="dlg-event">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="saveEvent()" style="width:100px">Сохранить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript: \$('#dlg_event').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма добавления нового мероприятия -->
    
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