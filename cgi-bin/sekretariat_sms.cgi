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
use XML::Simple;
use LWP::UserAgent;

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
my $SMS_SEKRETARIAT=$sess->param('SMS_SEKRETARIAT');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

    if ($SMS_SEKRETARIAT==1) #Смотрим имеет ли доступ пользователь к модулю "СМС".
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

        #Получение баланса СМС сервиса в руб.
        my $cgi=CGI->new;
        my @res;

        #Определяем есть ли запись в БД о логине и пароле СМС шлюза
        my $data;
        my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
        my $sth=$dbh->do("SET NAMES 'cp1251'");
        my $sql="select LOGIN, PASSW from sms_gate";
        $sth=$dbh->prepare($sql);
        $sth->execute();
        my @row_gate = $sth->fetchrow_array;
        #################################################

        #Получаем непосредственно баланс с СМС-шлюза
        my $ua = new LWP::UserAgent;
 
        my $login = $row_gate[0];
        my $password = $row_gate[1];
 
        my $get_balance = '<?xml version="1.0" encoding="UTF-8"?><SMS>
                           <operations>
                           <operation>BALANCE</operation>
                           </operations>
                           <authentification>
                           <username>'.$login.'</username>
                           <password>'.$password.'</password>
                           </authentification>
                           </SMS>';
 
        my $response = $ua->post('http://api.atompark.com/members/sms/xml.php',{ XML => $get_balance});

        my $bal= XML::Simple->new()->XMLin($response->content);

        my $balance;
        if ($bal->{amount}) { $balance="(Баланс: ".$bal->{amount}." руб.)"; } else { $balance=""; }


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
	   
	   <script>//Включение Keyboard Navigation
        \$(function(){
            
        \$('#dg_debts').datagrid('getPanel').panel('panel').attr('tabindex',0).bind('keydown',function(e){
	 switch(e.keyCode){
		case 38:	// up
			var selected = \$('#dg_debts').datagrid('getSelected');
			if (selected){
				var index = \$('#dg_debts').datagrid('getRowIndex', selected);
				\$('#dg_debts').datagrid('selectRow', index-1);
			} else {
				\$('#dg_debts').datagrid('selectRow', 0);
			}
			break;
		case 40:	// down
			var selected = \$('#dg_debts').datagrid('getSelected');
			if (selected){
				var index = \$('#dg_debts').datagrid('getRowIndex', selected);
				\$('#dg_debts').datagrid('selectRow', index+1);
			} else {
				\$('#dg_debts').datagrid('selectRow', 0);
			}
			break;
	                }
                });
       
        \$('#dg_debts_month').datagrid('getPanel').panel('panel').attr('tabindex',0).bind('keydown',function(e){
	 switch(e.keyCode){
		case 38:	// up
			var selected = \$('#dg_debts_month').datagrid('getSelected');
			if (selected){
				var index = \$('#dg_debts_month').datagrid('getRowIndex', selected);
				\$('#dg_debts_month').datagrid('selectRow', index-1);
			} else {
				\$('#dg_debts_month').datagrid('selectRow', 0);
			}
			break;
		case 40:	// down
			var selected = \$('#dg_debts_month').datagrid('getSelected');
			if (selected){
				var index = \$('#dg_debts_month').datagrid('getRowIndex', selected);
				\$('#dg_debts_month').datagrid('selectRow', index+1);
			} else {
				\$('#dg_debts_month').datagrid('selectRow', 0);
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
       
       <script> //Подсчет кол-ва введенных символов
       \$(function(){      
        \$('#sms_text').textbox({
	inputEvents:\$.extend({},\$.fn.textbox.defaults.inputEvents,{
		keyup:function(e){
			var st=\$('#sms_text').textbox('getText');
			var res=st.length;
			var cnt_sms=parseInt(res/70)+1;			
			\$('#cnt_symbol').text("Введено "+res+" символов, кол-во СМС: "+cnt_sms);			
		    }
	      })
        })   
		////////////////////////////////////////
		
		\$('#sms_text_teacher').textbox({
	    inputEvents:\$.extend({},\$.fn.textbox.defaults.inputEvents,{
		keyup:function(e){
			var st1=\$('#sms_text_teacher').textbox('getText');
			var res1=st1.length;
			var cnt_sms1=parseInt(res1/70)+1;
			\$('#cnt_symbol_teacher').text("Введено "+res1+" символов, кол-во СМС: "+cnt_sms1);			
		    }
	      })
        })
        ////////////////////////////////////
		
                  });
        </script>
        
        <script>
        function open_window_select_stud(){
           \$('#dlg_select_student').window('open').dialog('center').dialog('setTitle','Выбор студентов для отправки СМС');
           \$('#dg_select_student').datagrid({url: 'get_students_4_send_sms.cgi?SID=$SID'});            
        }
		/////////////////////////////////////////////
		
		function open_window_select_teachers(){
           \$('#dlg_select_teacher').window('open').dialog('center').dialog('setTitle','Выбор преподавателей для отправки СМС');
           \$('#dg_select_teachers').datagrid({url: 'get_teachers_4_send_sms.cgi?SID=$SID'});            
        }
        </script>
        
        <script> //Вывод кол-ва выделенных студентов
        \$(function(){
        \$('#dg_select_student').datagrid({
        onSelect:function(index){
                                 var rows = \$('#dg_select_student').datagrid('getSelections');
                                 \$('#lb_stud').text('Кол-во выбранных студентов:'+rows.length);        
                                },
        onUnselect:function(index){
                                 var rows = \$('#dg_select_student').datagrid('getSelections');
                                 \$('#lb_stud').text('Кол-во выбранных студентов:'+rows.length);        
                                },
        onSelectAll:function(index){
                                 var rows = \$('#dg_select_student').datagrid('getSelections');
                                 \$('#lb_stud').text('Кол-во выбранных студентов:'+rows.length);        
                                },
        onUnselectAll:function(index){
                                 var rows = \$('#dg_select_student').datagrid('getSelections');
                                 \$('#lb_stud').text('Кол-во выбранных студентов:'+rows.length);        
                                }
                        });
		///////////////////////////////////////////////////////
		
		\$('#dg_select_teachers').datagrid({
        onSelect:function(index){
                                 var rows1 = \$('#dg_select_teachers').datagrid('getSelections');
                                 \$('#lb_teachers').text('Кол-во выбранных преподавателей:'+rows1.length);        
                                },
        onUnselect:function(index){
                                 var rows1 = \$('#dg_select_teachers').datagrid('getSelections');
                                 \$('#lb_teachers').text('Кол-во выбранных преподавателей:'+rows1.length);        
                                },
        onSelectAll:function(index){
                                 var rows1 = \$('#dg_select_teachers').datagrid('getSelections');
                                 \$('#lb_teachers').text('Кол-во выбранных преподавателей:'+rows1.length);        
                                },
        onUnselectAll:function(index){
                                 var rows1 = \$('#dg_select_teachers').datagrid('getSelections');
                                 \$('#lb_teachers').text('Кол-во выбранных преподавателей:'+rows1.length);        
                                }
        });
        ///////////////////////////////////////////////////////////////////////////////////////
						
        });
        </script>
        
       <script>//Установка фильтра для формы выбора студента для отправки СМС
       function doFilter_4_send_sms(){
       
       //Проверка, выбран хотя бы один параметр фильтрации
       if((!\$("#radio_DATE_OF_DOGOVOR").prop("checked")) && (!\$("#radio_KIND_PROG").prop("checked")) && (!\$("#radio_erase_filter_tie").prop("checked"))) {
	    \$.messager.alert('Внимание','Не выбран параметр фильтрации!','warning');
	    return;
        }        
               
       ///////////////////
       if(\$("#radio_DATE_OF_DOGOVOR").prop("checked")) { 
              \$('#dg_select_student').datagrid('load',{
              date_of_dogovor_from: \$('#DATE_OF_DOGOVOR_FROM').datebox('getValue'),
              date_of_dogovor_to: \$('#DATE_OF_DOGOVOR_TO').datebox('getValue')             
              });
              \$('#lb_tie').text('Установлен фильтр по "Дата договора"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_KIND_PROG").prop("checked")) { 
              \$('#dg_select_student').datagrid('load',{
              kind_prog: \$('#KIND_PROG').combobox('getValue'),
              });
              \$('#lb_tie').text('Установлен фильтр по "Программа"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_erase_filter_tie").prop("checked")) { 
              \$('#dg_select_student').datagrid('load',{
              erase_filter: 'switch_filter'
              });
              \$('#lb_tie').text('');
       }
       ///////////////////
 
       \$('#fm_filter_4_send_sms').form('clear'); \$('#dlg_filter_4_send_sms').dialog('close'); //Закрываем и форму фильтрации и очищаем поля
 
       }
       </script>//Конец скрипта установки фильтра для формы выбора студента для отправки СМС       
       
       <script>
       function add_selected_students(){
            var rows = \$('#dg_select_student').datagrid('getSelections');            
            for(var i=0; i<rows.length; i++)
            {
                var row = rows[i];
                \$('#dg_selected_students').datagrid('insertRow',{index: i, row: {Num_dogovor: row.Num_dogovor, FIO: row.FIO, MOBILE_PHONE: row.MOBILE_PHONE}  });    
                
            }      
            \$('#dlg_select_student').dialog('close');                        
       }
       </script>
	   
	   <script>
       function add_selected_teachers(){
            var rows1 = \$('#dg_select_teachers').datagrid('getSelections');            
            for(var i1=0; i1<rows1.length; i1++)
            {
                var row1 = rows1[i1];
                \$('#dg_selected_teachers').datagrid('insertRow',{index: i1, row: {FIO: row1.FIO, PHONE: row1.PHONE}  });    
                
            }      
            \$('#dlg_select_teacher').dialog('close');                        
       }
       </script>
       
       <script>
       \$(function(){
       \$('#dg_selected_students').datagrid({
	   width:'100%',
	   height:'100%',
	   singleSelect:true,
	   showHeader:false,
	   columns:[[
            {field:'Num_dogovor',title:'№Договора',width:50},	   
	        {field:'FIO',title:'ФИО',width:230},
			{field:'MOBILE_PHONE',title:'Моб.тел.',width:120},
			{field:'action',title:'Action',width:80,align:'center',	formatter:function(value,row,index){return '<a href="javascript:void(0)" onclick="deleterow(this)">Удалить</a>'}}
		   ]]
		});
		////////////////////////////
		
		\$('#dg_selected_teachers').datagrid({
	    width:'100%',
	    height:'100%',
	    singleSelect:true,
	    showHeader:false,
	    columns:[[	               
	        	{field:'FIO',title:'ФИО',width:250},
			{field:'PHONE',title:'Моб.тел.',width:120},
			{field:'action',title:'Action',width:80,align:'center',	formatter:function(value,row,index){return '<a href="javascript:void(0)" onclick="deleterow_tech(this)">Удалить</a>'}}
		   ]]
	    });
	    ///////////////////			
	    });
		
	function getRowIndex(target){
	        var tr = \$(target).closest('tr.datagrid-row');
		return parseInt(tr.attr('datagrid-row-index'));
	}
	
	function deleterow(target){
		\$.messager.confirm('Внимание','Вы уверены?',function(r){
		if (r){
			\$('#dg_selected_students').datagrid('deleteRow', getRowIndex(target));
	              }
		});
	}	

    function getRowIndex_tech(target){
	        var tr = \$(target).closest('tr.datagrid-row');
		return parseInt(tr.attr('datagrid-row-index'));
	}
	
	function deleterow_tech(target){
		\$.messager.confirm('Внимание','Вы уверены?',function(r){
		if (r){
			\$('#dg_selected_teachers').datagrid('deleteRow', getRowIndex_tech(target));
	              }
		});
	}	
	</script>
	
	<script> //Функция очистки списка адресатов для рассылки
	function clear_addr(){
              \$.messager.confirm('Внимание','Вы уверены, что необходимо очистить список адресатов для рассылки?',function(r){
              if (r){                  
                      \$('#dg_selected_students').datagrid('selectAll');                      
                      var list_addr = \$('#dg_selected_students').datagrid('getSelections');
                      for (var i = 0; i <= list_addr.length-1; i++)
                      {
                         idx = \$('#dg_selected_students').datagrid('getRowIndex', list_addr[i]);
                         \$('#dg_selected_students').datagrid('deleteRow',idx)
                      }                                                                                     
                    }
                });
            
        }  
	</script>
	
	<script> //Функция очистки списка преподов для рассылки
	function clear_addr_teachers(){
              \$.messager.confirm('Внимание','Вы уверены, что необходимо очистить список преподавателей для рассылки?',function(r){
              if (r){                  
                      \$('#dg_selected_teachers').datagrid('selectAll');                      
                      var list_addr = \$('#dg_selected_teachers').datagrid('getSelections');
                      for (var i = 0; i <= list_addr.length-1; i++)
                      {
                         idx = \$('#dg_selected_teachers').datagrid('getRowIndex', list_addr[i]);
                         \$('#dg_selected_teachers').datagrid('deleteRow',idx)
                      }                                                                                     
                    }
                });
            
        }  
	</script>
	
	<script>
        function send_sms(){
            var rows_students = \$('#dg_selected_students').datagrid('getData'); 
            var checked = \$('#USE_DOG_FIO').switchbutton('options').checked;   			
            var ss = [];
            for (var i=0; i<=rows_students.rows.length-1; i++)
            {
			    var num_dog = rows_students.rows[i].Num_dogovor;
                var fio_stud = rows_students.rows[i].FIO; 
                var num_phone = rows_students.rows[i].MOBILE_PHONE;
                ss.push(num_phone);                
            }    
                               
            \$.ajax({            
            type: 'GET',
            traditional: true,
            url: 'send_sms.cgi?SID=$SID',
            data: {'data':ss, 'text_sms': \$('#sms_text').textbox('getText'), 'use_dog_fio': checked },
            success: function(res) {\$.messager.alert('Информация',res.result,'info');},
            error: function() {alert("did not work");}
            });            
                         
        }
        </script>
		
		<script>
        function send_sms_2_teachers(){
            var rows_teachers = \$('#dg_selected_teachers').datagrid('getData');                              
            var ss = [];
            for (var i=0; i<=rows_teachers.rows.length-1; i++)
            {
                var num_phone = rows_teachers.rows[i].PHONE;
                ss.push(num_phone);                
            }    
                               
            \$.ajax({            
            type: 'GET',
            traditional: true,
            url: 'send_sms_teachers.cgi?SID=$SID',
            data: {'data':ss, 'text_sms': \$('#sms_text_teacher').textbox('getText') },
            success: function(res) {\$.messager.alert('Информация',res.result,'info');},
            error: function() {alert("did not work");}
            });            
                         
        }
        </script>
		
		<script>
        function build_debts() {
        \$('#fd').linkbutton('enable');
		var checked_ind_common = \$('#INDIVIDUAL_COMMON').switchbutton('options').checked;
        \$.ajax({            
                         type: 'POST',
                         traditional: true,
                         url: 'get_debts_4_sms.cgi',
                         data: {'SID':'$SID', 'individual_common':checked_ind_common},
                         success: function(res) {                                              
                                                 \$('#dg_debts').datagrid('loadData', res.rows).datagrid('reloadFooter', res.footer);                                                 
                                                },
                         error: function() {alert("did not work");}
                  });                
          
         }
        </script>
        
        <script>
        function search_data() {
        var ffio = \$('#fio').val();
        var dogov = \$('#n_dogovor').val();
        var tech = \$('#TEACHER_ID').combobox('getValue');
        var checked_ind_common = \$('#INDIVIDUAL_COMMON').switchbutton('options').checked;      
        \$.ajax({            
                         type: 'POST',
                         traditional: true,
                         url: 'get_debts_4_sms.cgi',
                         data: {'fio':ffio, 'n_dogovor':dogov, 'teacher':tech, 'individual_common':checked_ind_common, 'SID':'$SID'},
                         success: function(res) {                                              
                                                 \$('#dg_debts').datagrid('loadData', res.rows).datagrid('reloadFooter', res.footer);                                                 
                                                },
                         error: function() {alert("did not work");}
                  });
                  
         if (\$('#TEACHER_ID').combobox('getValue').length>0)
         {           
             var v = \$('#TEACHER_ID').combobox('getText');
             \$('#lb').text('Установлен фильтр по: '+v);
         }
         else
         {
             \$('#lb').text('');
         }               
          
         }
        </script>
        
            
        <script>
        function send_sms_debts_today(){
            var rows_students_debts_today = \$('#dg_debts').datagrid('getData');                              
            var ss_debts_today = [];
            var incorrect_numbers=[];
            var status_message;
            for (var i1=0; i1<=rows_students_debts_today.rows.length-1; i1++)
            {
                var dog_debt_today = rows_students_debts_today.rows[i1].nm_dg;
				var fio_debt_today = rows_students_debts_today.rows[i1].fio;                
                var num_phone_debt_today = rows_students_debts_today.rows[i1].mobile_phone;
                var summ_debt_today = rows_students_debts_today.rows[i1].summ;                
                
                if (num_phone_debt_today.length<11) 
                {
                     incorrect_numbers.push('<br />'+fio_debt_today); //Заполняем массив ФИО студентов которым не будет отправлена СМС, т.к. у них не корректный номер
                     continue;
                }
                
                ss_debts_today.push(num_phone_debt_today, summ_debt_today, dog_debt_today); //Заполняем массив корректными номерами студентов и их суммами долга для отправки их в СМС
            }
            
                        
            if (incorrect_numbers.length>0)
            {
               status_message='Нижеуказанным студентам рассылка проведена не будет по причине отсутствия или некорректности мобильного номера!<b>'+ incorrect_numbers +'</b><br />Продолжить рассылку или отменить?';            
            }
            else
            {
               status_message='Вы уверены, что необходимо провести рассылку?';
            }
            
            \$.messager.confirm('Внимание', status_message, function(r){
                    if (r){
                               \$.ajax({            
                               type: 'GET',
                               traditional: true,
                               url: 'send_sms_debts_today.cgi?SID=$SID',
                               data: {'data':ss_debts_today},
                               success: function(res) {\$.messager.alert('Информация',res.result,'info');},
                               error: function() {alert("did not work");}
                               });                       
                          }
                    });
                                                        
                       
                         
        }
        </script>
		
		<script>
        function make_report() {
          var mth=\$('#month').combobox('getValue');
          var tech=\$('#TEACHER_ID_month').combobox('getValue');
		  var ye=\$('#year').combobox('getValue');
		  var checked_ind = \$('#INDIVIDUAL').switchbutton('options').checked;
          \$.ajax({            
                         type: 'POST',
                         traditional: true,
                         url: 'get_debts_month_4_sms.cgi',
                         data: {'month':mth, 'year':ye, 'teacher':tech, 'individual': checked_ind, 'SID':'$SID'},            
                         success: function(res) {                                              
                                                 \$('#dg_debts_month').datagrid('loadData', res.rows).datagrid('reloadFooter', res.footer);                                                 
                                                },
                         error: function() {alert("did not work");}
                  });
                  
          if (\$('#TEACHER_ID_month').combobox('getValue').length>0)
          {           
           var v = \$('#TEACHER_ID_month').combobox('getText');
           \$('#lb_month').text('Должники по: '+v);
          }
          else
          {
           \$('#lb_month').text('');
          }
                     
         }
        </script>
        
        
        <script>
        function send_sms_debts_month(){
            var rows_students_debts_month = \$('#dg_debts_month').datagrid('getData');                              
            var ss_debts_month = [];
            var incorrect_numbers_month=[];
            var status_message_month;
            for (var i2=0; i2<=rows_students_debts_month.rows.length-1; i2++)
            {
			    var dog_debt_month = rows_students_debts_month.rows[i2].nm_dg;
                var fio_debt_month = rows_students_debts_month.rows[i2].fio;                
                var num_phone_debt_month = rows_students_debts_month.rows[i2].mobile_phone;
                var summ_debt_month = rows_students_debts_month.rows[i2].summ;                
                
                if (num_phone_debt_month.length<11) 
                {
                     incorrect_numbers_month.push('<br />'+fio_debt_month); //Заполняем массив ФИО студентов которым не будет отправлена СМС, т.к. у них не корректный номер
                     continue;
                }
                
                ss_debts_month.push(num_phone_debt_month, summ_debt_month, dog_debt_month); //Заполняем массив корректными номерами студентов и их суммами долга для отправки их в СМС
            }
            
                        
            if (incorrect_numbers_month.length>0)
            {
               status_message_month='Нижеуказанным студентам рассылка проведена не будет по причине отсутствия или некорректности мобильного номера!<b>'+ incorrect_numbers_month +'</b><br />Продолжить рассылку или отменить?';            
            }
            else
            {
               status_message_month='Вы уверены, что необходимо провести рассылку?';
            }
            
            \$.messager.confirm('Внимание', status_message_month, function(r){
                    if (r){
                               \$.ajax({            
                               type: 'GET',
                               traditional: true,
                               url: 'send_sms_debts_month.cgi?SID=$SID',
                               data: {'data':ss_debts_month},
                               success: function(res) {\$.messager.alert('Информация',res.result,'info');},
                               error: function() {alert("did not work");}
                               });                       
                          }
                    });
                                                        
                       
                         
        }
        </script>
		
		<script>
        \$(function(){
            var Data=[];
            var now = new Date();
            var present_year=now.getFullYear();
            var prev_year=now.getFullYear()-1;
            Data.push({"id":prev_year,"name":prev_year}, {"id":present_year,"name":present_year});
            \$('#year').combobox({data:Data});
            \$('#year').combobox('setValue', present_year);
        });
        </script>
		
		<script>
        \$(function(){
        \$('#USE_DOG_FIO').switchbutton({            
            onChange: function(checked){
                if (checked)
                {
                    \$('#lb_dg').text('Для добавления в текст СМС №договора и ФИО используйте ключи: %1% - №договора, %2% - ФИО.');
                }
                else
                {
                    \$('#lb_dg').text('');
                }                
            }
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
        <div data-options="region:'center',title:'Рабочая область - СМС рассылки $balance. Пользователь: $formLogin'">
        
           <!-- Список табов для отображения СМС рассылок --> 
           <div id="tabs_sms" class="easyui-tabs" data-options="pill:true, justified:true" style="width:100%;height:100%">
              
              <div title="Простая рассылка" style="padding:10px">
              
                 <!-- Внутрненний layout для отправки СМС --> 
                 <div class="easyui-layout" style="width:100%;height:100%;">
                    
                    <!-- Субправый DIV раздел подробности -->
                   <div data-options="region:'east',split:true" title="Список выбранных адресатов" style="width:30%;">                   
                     
                     <table id="dg_selected_students"></table>
                    
                   </div>
                   <!-- Конец Субправый DIV раздел подробности -->
             
                   <!-- Субцентральный DIV -рабочая область -->
                   <div data-options="region:'center'" title="Создать рассылку СМС">
                      
                      <div style="margin:10px 0 0 10px;">
                        <a href="#" class="easyui-linkbutton" style="width:150px;" iconCls="icon-man" onclick="open_window_select_stud()">Выбор адресатов</a>
                        <br />
                        <div style="margin-top:20px;">
                          <input id="sms_text" class="easyui-textbox" data-options="prompt:'Введите текст СМС сообщения...'" multiline="true" style="width:80%;height:120px;">
                        </div>
                        <br />
                        <div style="margin-top:-10px;">
                          <span id="cnt_symbol" style="font-weight: bold;">Введено 0 символов, кол-во СМС: 1</span>
                        </div>
						<label>Использовать №договора и ФИО в тексте СМС?:</label>                        
               	        <input id="USE_DOG_FIO" name="USE_DOG_FIO" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">
               	        <br />
               	        <span id="lb_dg" style="float:left; color: #F00; font-weight: bold;"></span>
               	        <br />               	        
                        <a href="#" class="easyui-linkbutton" style="width:150px;" iconCls="icon-sms" onclick="send_sms()">Отправить</a>
                        <a href="#" class="easyui-linkbutton" style="width:170px;" iconCls="icon-del_list" onclick="clear_addr()">Очистить рассылку</a>                        
                      </div>
                   
                   
                   </div>
                   <!-- Конец Субцентральный DIV -рабочая область -->
                 
                 </div>
                 <!-- Конец Внутрненний layout для отправки СМС --> 
              
              </div>
              
              <div title="Рассылка должникам" style="padding:10px">
			  
			      <!-- Список табов для отображения разделов должников --> 
                  <div id="tabs_debts" class="easyui-tabs" data-options="pill:true, justified:true, fit:true" style="width:100%;height:100%">
                      
                      <div title="Должники на сегодня" style="padding:10px">
                      
                         <a href="#" class="easyui-linkbutton" style="width:150px; margin-bottom:10px;" iconCls="icon-document" onclick="build_debts()">Сформировать</a>
                         <div style="margin-left:10px; margin-bottom:5px; color: #F00; font-weight: bold;">
                         <label>Исключить индивидуальщиков из рассылки:</label>
               	         <input id="INDIVIDUAL_COMMON" name="INDIVIDUAL_COMMON" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">              	        
                         </div>                         
                         
                         <table id="dg_debts" title="Должники на сегодня" class="easyui-datagrid" style="width:100%;height:85%"
                         method="get"                         
                         toolbar="#tb"
                         rownumbers="true" fitColumns="true" singleSelect="true" sortName="nm_dg" sortOrder="asc" showFooter="true">

                         <thead>
                         <tr>
                             <th field="nm_dg" width="20" sortable="true">Договор</th>
                             <th field="fio" width="167" sortable="true">ФИО</th>
                             <th field="mobile_phone" width="50">Моб.телефон.</th>                             
                             <th field="summ" width="30">Сумма</th>            
                             <th field="name" width="30"></th>
                             <th field="count" width="30"></th>            
                         </tr>
                         </thead>
                         </table>        
              
                         <!-- Панель посика -->
                         <div id="tb" style="padding:3px">
                         <span>Поиск по ФИО:</span>
                         <input id="fio" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
                         <span>Поиск по договору:</span>
                         <input id="n_dogovor" class="easyui-numberbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">             
                         <span>Поиск по Преподавателю:</span>
                         <input id="TEACHER_ID" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_teacher_4_lessons.cgi?SID=$SID', method: 'get', icons:[{iconCls:'icon-clear', handler: function(e){var v = \$(e.data.target).combobox('clear');} }]   ">
                         <a href="#" id="fd" class="easyui-linkbutton" plain="false" disabled="true" onclick="search_data()" style="border-radius:5px; width:100px;">Искать</a>
                         <span id="lb" style="color: #F00; font-weight: bold;"></span>                                               
                         </div>
                         <!-- Конец Панель для поиска -->
                         <br />
                         <a href="#" class="easyui-linkbutton" style="width:350px; margin-left:40%;" iconCls="icon-sms" onclick="send_sms_debts_today()">Отправить</a>
                         
                      
                      </div>
                      
                      <div title="Должники за месяц" style="padding:10px">   

                        <table id="dg_debts_month" title="Должники за месяц" class="easyui-datagrid" style="width:100%;height:90%"
                        method="get"
                        url=""
                        toolbar="#tb_month"
                        rownumbers="true" fitColumns="true" singleSelect="true" sortName="nm_dg" sortOrder="asc" showFooter="true">
                        
                        <thead> 
                         <tr>
                           <th field="nm_dg" width="20" sortable="true">Договор</th>
                           <th field="fio" width="167" sortable="true">ФИО</th>
                           <th field="mobile_phone" width="50">Моб.телефон.</th>                                                          
                           <th field="summ" width="30">Сумма</th>            
                           <th field="name" width="30"></th>
                           <th field="count" width="30"></th>            
                         </tr>
                        </thead> 
                        </table>        
              
                        <!-- Панель посика -->
                        <div id="tb_month" style="padding:3px">
                        <div style="margin-top:5px; margin-bottom:5px">
                        <span>Сформировать должников за месяц:</span>
                        <select id="month" class="easyui-combobox" name="month" style="width:100px">
                        <option value="1">Январь</option>
                        <option value="2">Февраль</option>
                        <option value="3">Март</option>
                        <option value="4">Апрель</option>
                        <option value="5">Май</option>
                        <option value="6">Июнь</option>
                        <option value="7">Июль</option>
                        <option value="8">Август</option>
                        <option value="9">Сентябрь</option>
                        <option value="10">Октябрь</option>
                        <option value="11">Ноябрь</option>
                        <option value="12">Декабрь</option>             
                        </select>
						<input id="year" name="year" class="easyui-combobox" data-options="editable:false, valueField:'id',textField:'name'">
                        <span>    По преподавателю:</span>
                        <input id="TEACHER_ID_month" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_teacher_4_lessons.cgi?SID=$SID', method: 'get', icons:[{iconCls:'icon-clear', handler: function(e){var v = \$(e.data.target).combobox('clear');} }]   ">
                        <a href="#" class="easyui-linkbutton" plain="false" onclick="make_report()" style="border-radius:5px; width:100px;">Сформировать</a>             
                        <span id="lb_month" style="color: #F00; font-weight: bold;"></span>    
                        <br />
                        <div style="margin-top:10px; margin-left:10px; color: #F00; font-weight: bold;">
                           <label>Исключить индивидуальщиков из рассылки:</label>
               	           <input id="INDIVIDUAL" name="INDIVIDUAL" class="easyui-switchbutton" value="1" data-options="onText:'Да',offText:'Нет'">              	        
                        </div>						
                        </div>                       
                        </div>
                        <!-- Конец Панель для поиска -->
                        <br />
                        <a href="#" class="easyui-linkbutton" style="width:350px; margin-left:40%;" iconCls="icon-sms" onclick="send_sms_debts_month()">Отправить</a>   
					  
                      </div>
                      
                  </div>
                  <!-- Конец список табов для отображения разделов должников --> 
			  
              </div>
              
              <div title="Рассылка преподавателям" style="padding:10px">
			  
                    <!-- Внутрненний layout для отправки СМС --> 
                    <div class="easyui-layout" style="width:100%;height:100%;">
                    
                    <!-- Субправый DIV раздел подробности -->
                    <div data-options="region:'east',split:true" title="Список выбранных преподавателей" style="width:30%;">                   
                     
                     <table id="dg_selected_teachers"></table>
                    
                    </div>
                    <!-- Конец Субправый DIV раздел подробности -->
             
                   <!-- Субцентральный DIV -рабочая область -->
                   <div data-options="region:'center'" title="Создать рассылку СМС для преподавателей">
                      
                      <div style="margin:10px 0 0 10px;">
                        <a href="#" class="easyui-linkbutton" style="width:150px;" iconCls="icon-man" onclick="open_window_select_teachers()">Выбор адресатов</a>
                        <br />
                        <div style="margin-top:20px;">
                          <input id="sms_text_teacher" class="easyui-textbox" data-options="prompt:'Введите текст СМС сообщения...'" multiline="true" style="width:80%;height:120px;">
                        </div>
                        <br />
                        <div style="margin-top:-10px;">
                          <span id="cnt_symbol_teacher" style="font-weight: bold;">Введено 0 символов, кол-во СМС: 1</span>
                        </div>
                        <a href="#" class="easyui-linkbutton" style="width:150px;" iconCls="icon-sms" onclick="send_sms_2_teachers()">Отправить</a>
                        <a href="#" class="easyui-linkbutton" style="width:170px;" iconCls="icon-del_list" onclick="clear_addr_teachers()">Очистить рассылку</a>                        
                      </div>
                   
                   
                   </div>
                   <!-- Конец Субцентральный DIV -рабочая область -->
                 
                 </div>
                 <!-- Конец Внутрненний layout для отправки СМС --> 
			  
              </div>
           
           </div>
           <!-- Конец Список табов для отображения справочников -->
    
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
    
    <!-- Форма выбора студентов для отправки СМС -->    
    <div id="dlg_select_student" class="easyui-dialog" style="width:450px;height:500px;padding:10px 5px 0px 5px;"
            closed="true" modal="true" buttons="#dlg-buttons_stud" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <span id="lb_stud" style="float:left; font-weight: bold; margin-bottom:10px;">Кол-во выбранных студентов:</span>
        <table id="dg_select_student" class="easyui-datagrid" style="width:100%;height:75%"
        method="get" fitColumns="true" sortName="FIO" sortOrder="asc" striped=true>

        <thead>
        <tr>
            <th field="ck_bx" checkbox="true"></th>
            <th field="Num_dogovor" width="40" sortable="true">Договор</th>
            <th field="FIO" width="110" sortable="true">ФИО</th>
            <th field="MOBILE_PHONE" width="60" sortable="true">Моб.телефон</th>                                    
        </tr>
        </thead>
        </table>
        <!--Кнопка фильтра -->
            <div style="padding:10px 10px;">
            <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-filter'" onclick="\$('#dlg_filter_4_send_sms').window('open').dialog('center').dialog('setTitle','Фильтр')">Фильтр</a>
            </div>
        <!--Конец Кнопка фильтра -->
        <span id="lb_tie" style="float:right; color: #F00; font-weight: bold;"></span>
    </div> 
    <div id="dlg-buttons_stud">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="add_selected_students()" style="width:100px">Ок</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_select_student').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма выбора студентов для отправки СМС -->
    
    <!-- Форма установки фильтра при выборе студента для отправки СМС -->    
    <div id="dlg_filter_4_send_sms" class="easyui-dialog" style="width:500px;height:220px;padding:10px 1px;"
            closed="true" modal="true" buttons="#dlg-buttons_4_send_sms" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Установка фильтра</div>
        <form id="fm_filter_4_send_sms" novalidate>
            <table>
                 <tr>
                    <td><label><input id="radio_DATE_OF_DOGOVOR" name="radio" type="radio" value="0" />Дата договора:    От--</label></td>
                    <td><input id="DATE_OF_DOGOVOR_FROM" name="DATE_OF_DOGOVOR_FROM" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser">   До--<input id="DATE_OF_DOGOVOR_TO" name="DATE_OF_DOGOVOR_TO" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser"></td>
                </tr>               
                <tr>                    
                    <td><label><input id="radio_KIND_PROG" name="radio" type="radio" value="1" />Программа:</label></td>
                    <td><input id="KIND_PROG" name="KIND_PROG" class="easyui-combobox" style="width:330px;" data-options="editable:false, panelHeight:'300px', valueField: 'id', valueText: 'text', groupField:'group', url: 'get_kind_prog.cgi?SID=$SID', method: 'get'"></input></td>
                </tr>                
                <tr>
                    <td><label><input id="radio_erase_filter_tie" name="radio" type="radio" value="9" /><strong>Снять фильтры:</strong></label></td>                    
                </tr>
            </table>    
        </form>
    </div>
    <div id="dlg-buttons_4_send_sms">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="doFilter_4_send_sms()" style="width:100px">Установить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_filter_4_send_sms').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма установки фильтра при выборе студента для отпраки СМС -->
	
	<!-- Форма выбора преподов для отправки СМС -->    
    <div id="dlg_select_teacher" class="easyui-dialog" style="width:450px;height:500px;padding:10px 5px 0px 5px;"
            closed="true" modal="true" buttons="#dlg-buttons_teachers" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <span id="lb_teachers" style="float:left; font-weight: bold; margin-bottom:10px;">Кол-во выбранных преподавателей:</span>
        <table id="dg_select_teachers" class="easyui-datagrid" style="width:100%;height:75%"
        method="get" fitColumns="true" sortName="FIO" sortOrder="asc" striped=true>

        <thead>
        <tr>
            <th field="ck_bx" checkbox="true"></th>
            <th field="FIO" width="110" sortable="true">ФИО</th>
            <th field="PHONE" width="60" sortable="true">Моб.телефон</th>                                    
        </tr>
        </thead>
        </table>      
    </div> 
    <div id="dlg-buttons_teachers">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="add_selected_teachers()" style="width:100px">Ок</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_select_teacher').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма выбора преподов для отправки СМС -->
    
    
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