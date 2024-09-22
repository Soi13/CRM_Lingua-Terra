#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
#use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI::Session;
use CGI qw(:cgi);
use Digest::MD5 qw(md5_hex);
use Encode;

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
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:spending",User=>"root", Password=>""}) or die CGI::Session->errstr();
$sess->name('SID');

#Если сессия пустая
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

#Если вермя сессии истекло
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

#Если IP не совпадают
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

#Присваиваем переменным логин и пароль пользователя из сессии
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {
   
        #Подгружаем название личный кабинет для вывода ее на странице
        open FF, "<txt_data/pers_room.txt";
        my @pers_room=<FF>;
        foreach my $str (@pers_room)
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
        <title>@pers_room</title>
        <link rel="stylesheet" type="text/css" href="../CSS/easyui.css">
        <link rel="stylesheet" type="text/css" href="../CSS/icon.css">
        <link rel="stylesheet" type="text/css" href="../CSS/demo.css">
        <link rel="stylesheet" href="../CSS/styles.css">
        <script type="text/javascript" src="../JS/jquery.min.js"></script>
        <script type="text/javascript" src="../JS/jquery.easyui.min.js"></script>
        <script src="../JS/script.js"></script>
        <script type="text/javascript" src="../JS/datagrid-detailview.js"></script> 
        <script type="text/javascript" src="../JS/datagrid-cellediting.js"></script>
       
        
              
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
                window.location.replace("http://teachers.localhost:6080")}
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
       //group: \$('#group').val()
       group: \$('#group').textbox('getText')
       });
       }
       </script>

       <script>
       \$(function(){
       \$('#ls').hide(); 
       \$('#ph').hide();
       \$('#toolbar_homework').hide();  
       
       \$('#dg').datagrid({
       onSelect:function(index){          
       \$('#ls').hide(); 
       \$('#ph').hide();
       \$('#toolbar_homework').hide(); 
       \$('#list_of_students_visits').datagrid().datagrid('disableCellEditing');
               
       var row = \$('#dg').datagrid('getSelected');       
       //Загружаем и заполняем подробности по группам
       \$('#pg').propertygrid({
       method:'get',
       url: 'get_groups_detail.cgi?id_z='+row.ID+'&SID=$SID',
       showGroup: true,
       showHeader: false,
       scrollbarSize: 0
       });
       //////////////////////////////////////////
       
       //Загружаем и выводим список периодов обучения студентов в группе
       \$('#periods').combobox({
       method:'get',
       panelHeight:'auto',
       editable: false,
       url:'get_periods_4_group.cgi?id_group='+row.ID+'&SID=$SID',
       valueField:'id',
       textField:'text'
       });    
       //////////////////////////////////////////
       
       //Загружаем и выводим список занятий группы
       \$('#list_of_lessons').datagrid({
       method:'get',
       title: 'Аудитория',
       showHeader: false,       
       scrollbarSize: 0,
       border: false,
       singleSelect: true,
       url:'get_lessons_in_group.cgi?id_z2='+row.ID+'&SID=$SID',
       columns:[[
                 {field:'ID',title:'ID', hidden:true},                 
                 {field:'ROOM',title:'<b>Аудитория</b>'}                                  
               ]]
       });       
       //////////////////////////////////////////
       
        
        //Загружаем и выводим список времени и дат занятий группы
       \$('#list_of_periods_of_lessons').datagrid({       
       method:'get',
       showHeader: true,       
       scrollbarSize: 0,
       striped: true,
       border: false,
       singleSelect: true,
       url:'get_list_lessons_in_group.cgi?id_z3='+row.ID+'&SID=$SID',
       columns:[[
                 {field:'ID',title:'ID', hidden:true},
                 {field:'WEEK_DAY',title:'<b>День недели</b>'},
                 {field:'DATE_LESSON',title:'<b>Дата занятия</b>'},
                 {field:'TIME_BEGIN',title:'<b>Время начала</b>'},
                 {field:'TIME_END',title:'<b>Время окончания</b>'}                                  
               ]]
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
       if((!\$("#radio_LANGUAGE").prop("checked")) && (!\$("#radio_LEVEL_KNOWLEDGE").prop("checked")) && (!\$("#radio_GROUP_TYPE").prop("checked")) && (!\$("#radio_TYPE_CALC_LESSON").prop("checked")) && (!\$("#radio_COUNT_CLASSES").prop("checked")) && (!\$("#radio_DURATION_CLASSES").prop("checked")) && (!\$("#radio_COURSE_PRICE").prop("checked")) && (!\$("#radio_TYPE_PAY").prop("checked")) && (!\$("#radio_KIND_PROGRAMM").prop("checked")) && (!\$("#radio_BRANCH").prop("checked")) && (!\$("#radio_ROOM").prop("checked")) && (!\$("#radio_erase_filter").prop("checked"))) {
	    \$.messager.alert('Внимание','Не выбран параметр фильтрации!','warning');
	    return;
        }        
               
       ///////////////////
       if(\$("#radio_LANGUAGE").prop("checked")) { 
              \$('#dg').datagrid('load',{
             language: \$('#LANGUAGE').combobox('getValue')                                          
              });
              \$('#lb').text('Установлен фильтр по "Курс"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_LEVEL_KNOWLEDGE").prop("checked")) { 
              \$('#dg').datagrid('load',{
             level_knowledge: \$('#LEVEL_KNOWLEDGE').combobox('getValue')
              });
              \$('#lb').text('Установлен фильтр по "Уровень"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_KIND_PROGRAMM").prop("checked")) { 
              \$('#dg').datagrid('load',{
             kind_programm: \$('#KIND_PROGRAMM').combobox('getValue')
              });
              \$('#lb').text('Установлен фильтр по "Программа"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_GROUP_TYPE").prop("checked")) { 
              \$('#dg').datagrid('load',{
             group_type: \$('#GROUP_TYPE').combobox('getValue')
              });
              \$('#lb').text('Установлен фильтр по "Тип группы"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_TYPE_CALC_LESSON").prop("checked")) { 
              \$('#dg').datagrid('load',{
             type_calc_lesson: \$('#TYPE_CALC_LESSON').combobox('getValue')
              });
              \$('#lb').text('Установлен фильтр по "Способ расчета занятий"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_COUNT_CLASSES").prop("checked")) { 
              \$('#dg').datagrid('load',{
             count_classes: \$('#COUNT_CLASSES').val()
              });
              \$('#lb').text('Установлен фильтр по "Кол-во занятий"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_DURATION_CLASSES").prop("checked")) { 
              \$('#dg').datagrid('load',{
             duration_classes: \$('#DURATION_CLASSES').val()
              });
              \$('#lb').text('Установлен фильтр по "Продолжительность занятий"');
       }
       ///////////////////
                            
       ///////////////////
       if(\$("#radio_COURSE_PRICE").prop("checked")) { 
              \$('#dg').datagrid('load',{
             course_price: \$('#COURSE_PRICE').val()
              });
              \$('#lb').text('Установлен фильтр по "Цена курса"');
       }
       ///////////////////
                    
       ///////////////////
       if(\$("#radio_TYPE_PAY").prop("checked")) { 
              \$('#dg').datagrid('load',{
             type_pay: \$('#TYPE_PAY').combobox('getValue')
              });
              \$('#lb').text('Установлен фильтр по "Вид расчета"');
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
       if(\$("#radio_ROOM").prop("checked")) { 
              \$('#dg').datagrid('load',{
             room: \$('#ROOM_filter').combobox('getValue')
              });
              \$('#lb').text('Установлен фильтр по "Аудитория"');
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
	var t = \$('#group');
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
        \$('#group').textbox({
	                      inputEvents:\$.extend({},\$.fn.textbox.defaults.inputEvents,{
		              keyup:function(e){
			                          doSearch();
		                               }
	                        })
                             })
        
        })
        </script>
        
        <script>
        \$(function(){         
          var conf = {            
            options:{
                fitColumns:true,
                rownumbers:true,
                showHeader:false,
                singleSelect:true,
                pagination:true,
                striped:true,
                columns:[[                    
                    {field:'ID',title:'ID',width:20, hidden:true},
                    {field:'GROUP_NAME',title:'Наименование группы',width:150}                                                          
                ]],                
                method: 'get',
                url:'get_groups.cgi?SID=$SID',
            },
            subgrid:{
                options:{
                    title: 'Студенты группы',
                    fitColumns:true,
                    rownumbers:true,
                    nowrap:false,
                    striped:true,
                    singleSelect:true,
                    foreignField:'id_gr',
                    foreignField:function(prow){
				return {
					id_gr: prow.ID
			        	}				
			},                    
                    columns:[[
                        {field:'Num_dogovor',title:'№ договора',width:50},
                        {field:'FIO',title:'ФИО',width:120}                         
                    ]],
                    method: 'get',
                    url:'get_detail_students_4_group.cgi?SID=$SID',
                }   
                
            }
          };  
         
          \$('#dg').datagrid().datagrid('subgrid', conf); 
         
          });        
        
        </script>

        
        <script>
        \$(function(){           
        \$('#periods').combobox({
	onSelect: function(){
	                       	var row_id_gr = \$('#dg').datagrid('getSelected');
	                       	var row_period = \$('#periods').combobox('getValue');
	                       	\$('#ls').show();
	                       	\$('#ph').show();
	                       	\$('#toolbar_homework').show();  	                       	
	                       	\$('#list_of_students_visits').datagrid().datagrid('disableCellEditing');
	                       	
	                       	 //Загружаем и выводим список посещений студентов в выбранном периоде
                                 \$('#list_of_students_visits').datagrid({
                                 title: 'Список студентов и их посещений',
                                 method:'get',                                
                                 showHeader: true,       
                                 scrollbarSize: 0,
                                 striped: true,
                                 border: false,
                                 clickToEdit: false,
                                 dblclickToEdit: true,
                                 singleSelect: true,
                                 url:'get_visits.cgi?idd_gr='+row_id_gr.ID+'&period='+row_period+'&SID=$SID',
                                 columns:[[
                                             {field:'ID',title:'ID', hidden:true},
                                             {field:'FIO',title:'<b>ФИО</b>'},                                                                                          
                                             {field:'DAY1',title:'<b>1</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY2',title:'<b>2</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY3',title:'<b>3</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY4',title:'<b>4</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY5',title:'<b>5</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY6',title:'<b>6</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY7',title:'<b>7</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY8',title:'<b>8</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY9',title:'<b>9</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY10',title:'<b>10</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY11',title:'<b>11</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY12',title:'<b>12</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY13',title:'<b>13</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY14',title:'<b>14</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY15',title:'<b>15</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY16',title:'<b>16</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY17',title:'<b>17</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY18',title:'<b>18</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY19',title:'<b>19</b>', editor:'text', styler:cellStyler},
											 {field:'DAY20',title:'<b>20</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY21',title:'<b>21</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY22',title:'<b>22</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY23',title:'<b>23</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY24',title:'<b>24</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY25',title:'<b>25</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY26',title:'<b>26</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY27',title:'<b>27</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY28',title:'<b>28</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY29',title:'<b>29</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY30',title:'<b>30</b>', editor:'text', styler:cellStyler},
                                             {field:'DAY31',title:'<b>31</b>', editor:'text', styler:cellStyler},
                                             {field:'NOTES',title:'<b>Примечания</b>', editor:'text'}                                         
                                         ]]
                                 });       
                                 //////////////////////////////////////////	 
                                 
                                 
                                 //Загружаем и выводим список пройденых тем и ДЗ
                                 \$('#home_work').datagrid({
                                 method:'get',  
                                 title: 'Пройденые темы/Домашние задания',                              
                                 showHeader: true,       
                                 scrollbarSize: 0,
                                 striped: true,
                                 border: false,
                                 singleSelect: true,
                                 fitColumns: true,                                 
                                 url:'get_homework.cgi?idd_gr_hw='+row_id_gr.ID+'&period_hw='+row_period+'&SID=$SID',
                                 columns:[[
                                             {field:'ID',title:'ID', hidden:true},
                                             {field:'DATE_LESSON',title:'<b>Дата занятия</b>'},
                                             {field:'TOPIC',title:'<b>Тема</b>'},
                                             {field:'HOME_WORK',title:'<b>ДЗ</b>'}                                                                                      
                                         ]]
                                 });       
                                 //////////////////////////////////////////                      		                       	
                                 
                                 
                                  \$('#list_of_students_visits').datagrid().datagrid('enableCellEditing');                                  
                                 
	                    }
                               });         
        });                
        </script>
        
        
        <script>
        \$(function(){        
        \$('#list_of_students_visits').datagrid({
	onEndEdit: function(index,row,changes){
	                              var cell = \$('#list_of_students_visits').datagrid('cell');  // current cell
	                              var current_field=cell.field;
	                              var current_index=cell.index;
	                              var current_changes=changes[current_field];
	                              
	                              if (current_changes.length>0 || current_changes=="")
	                              {
	                                 \$.ajax({            
                                         type: 'GET',
                                         traditional: true,
                                         url: 'update_visits.cgi?SID=$SID',
                                         data: {'curr_field':current_field, 'curr_id':row.ID, 'curr_changes':current_changes},
                                         success: function(res) {
                                                                  if (res.result!='true') {
                                                                                            \$.messager.alert('Информация',res.result, 'info');
                                                                                            \$('#list_of_students_visits').datagrid('updateRow',{
	                                                                                    index: current_index,
	                                                                                    row: {
		                                                                                    [current_field] : ''		                                                                                    
	                                                                                         }
                                                                                            });                   
                                                                                          }
                                                                },
                                         error: function() {alert("did not work");}
                                         });                     
                                      }
                            }
                               });
                               
                                        
        });                
        </script>
        
        <script>
        var url;
        function newTopic(){
             var row_id_gr = \$('#dg').datagrid('getSelected');
	     var row_period = \$('#periods').combobox('getValue');
	   	     
            \$('#dlg_topic_homework').dialog('open').dialog('center').dialog('setTitle','Новая тема и ДЗ');
            \$('#fm_topic_homework').form('clear');
            url = 'insert_topic_homework.cgi?SID=$SID&ident_gr='+row_id_gr.ID+'&ident_period='+row_period;
        }
        
        function editTopic(){
            var row = \$('#home_work').datagrid('getSelected');
            if (row){
	    \$('#dlg_topic_homework').dialog('open').dialog('center').dialog('setTitle','Редактирование темы и ДЗ');
            \$('#fm_topic_homework').form('load',row);               
            url = 'edit_topic_homework.cgi?id_x='+row.ID+'&SID=$SID';                                          
            }
        }
        
        function saveTopic() {
        var msg   = \$('#fm_topic_homework').serialize();
        \$.ajax({
          type: 'GET',
          url: url,
          data: msg,
          success: function(res) { \$.messager.alert('Информация',res.result,'info'); if (res.result=="Тема и ДЗ добавлены успешно!") {\$('#fm_topic_homework').form('clear'); \$('#dlg_topic_homework').dialog('close'); \$('#home_work').datagrid('reload');} if (res.result=="Тема и ДЗ отредактированы успешно!") {\$('#fm_topic_homework').form('clear'); \$('#dlg_topic_homework').dialog('close'); \$('#home_work').datagrid('reload');}},
          error: function() {alert("did not work");}
        });        
       }
                
       </script>
       
       <script>//Функция выделения цветом 
       \$(function(){
       
       \$('#list_of_lessons').datagrid({
	rowStyler: function(index,row){
			return 'background-color:#d9ecf2;'; // return inline style
			              }
        });
        
        });
        </script>
        
        <script> //Функция удаления группы
        function delTopic(){
            var row = \$('#home_work').datagrid('getSelected');
            if (row){
                \$.messager.confirm('Внимание','Вы уверены, что необходимо удалить выбранную тему и ДЗ?',function(r){
                    if (r){
                            \$.ajax({            
                            type: 'GET',
                            traditional: true,
                            url: 'delete_topic_homework.cgi?SID=$SID',
                            data: {'id_topic':row.ID},            
                            success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result=="Тема и ДЗ удалены успешно!") { \$('#fm_topic_homework').form('clear'); \$('#dlg_topic_homework').dialog('close'); \$('#home_work').datagrid('reload');}},
                            error: function() {alert("did not work");}
                            });                       
                  
                          }
                });
            }
        }  
        </script>
        
        <script>
        function cellStyler(value,row,index){
            if (value == '-'){
                return 'background-color:#ffee00;color:red;';
            }
            
            if (value == '+'){
                return 'background-color:#45f129;color:black;';
            }
        }
        </script>
		
		
       <script>
       \$(function(){
        var img = '<img src="../images/Excel.ico" style="width:20px;height:20px;align:left">';
        var txt = '<span style="line-height:21px;">Import to Excel</span>';
        \$('#excel').linkbutton({
                             text: img+txt
                            })
        });
        </script>
        
        <script>
        function exp_2_excel() {
        var myData = \$('#list_of_students_visits').datagrid('getData'); //???????? ?????? ? Datagrid ? ???????? ?? ? ?????? ? ??????? JSON
        var per=\$('#periods').combobox('getText');
        \$.ajax({            
                         type: 'POST',
                         traditional: true,
                         url: 'exp_2_excel_visits.cgi',
                         data: {'data':JSON.stringify(myData), 'period':per, 'SID':'$SID'},            
                         success: function(res) {\$.messager.alert('Information',res.result,'info');},
                         error: function() {alert("did not work");}
                  });
                     
         }
        </script>
        
        </head>
 
        
        <body class="easyui-layout">
        <!--Верхний DIV - заголовок -->
        <div data-options="region:'north',border:false" style="height:100px;background:#f0993c;padding:10px;"><h1 class="shd">@pers_room</h1>
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
HTML1
       
        #Подгружаем меню
        open FF2, "<txt_data/main_menu.txt";
        my @menu_panel=<FF2>;
        foreach my $str_menu (@menu_panel)
        {
           $str_menu=~s/\0//g;
           $str_menu=~s/\.\.//g;
           $str_menu=~s/[<]*script[^>]*>.*[<]*\/script[>]*//i; #На всяк случай удаляем тэги <script>
           $str_menu=~s/SID=\$SID/SID=$SID/i; #Подставляем регуляркой ссам SID в тексте вместо переменной $SID. Сам он не подставляется, т.к. кнопки грузятся из текстового файла.
        }
        close (FF2) or die $!;        
        print @menu_panel;
        #########################################    
       

        print <<HTML_e;
        </div>
        <!--КОнец Левый DIV раздел меню -->

        <!-- Правый DIV раздел подробности -->
        <div data-options="region:'east',split:true,title:'Подробности'" style="width:40%;padding:1px;">
        
         <!--Панель TABS -->
        <div class="easyui-tabs" style="width:100%; height:auto;" data-options="narrow:true, fit:true">
         <div title="Общие">
         <table id="pg" style="width:100%"></table>
         </div>
         <div title="Список занятий">              
           <table id="list_of_lessons" style="width:100%"></table>
           <table id="list_of_periods_of_lessons" style="width:100%"></table>           
         </div>          
         <div title="Посещаемость/Дом.задания">
           <div style="margin-left:10px; margin-top:10px;">
            <span><b>Выберите период обучения</b></span><br />
            <input id="periods" class="easyui-combobox" style="width:200px;">
           </div>
           <br />
           <div id="ls" style="margin-left:10px; margin-top:10px;">
                 <a id="excel" href="#" class="easyui-linkbutton" plain="true" onclick="exp_2_excel()" style="float:right">Excel</a>
                 <br />
            <table id="list_of_students_visits" style="width:100%"></table>
           </div>
           <div id="ph" style="margin-top:20px; margin-left:10px;">
             <table id="home_work" class="easyui-datagrid" style="width:100%" toolbar="#toolbar_homework"></table>
             <div id="toolbar_homework">
                <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="newTopic()">Добавить тему и ДЗ</a>
                <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="editTopic()">Редактировать тему и ДЗ</a>
                <a href="#" class="easyui-linkbutton" iconCls="icon-remove" plain="true" onclick="delTopic()">Удалить тему и ДЗ</a>                
             </div>            
           </div>
           
           
         </div>         
        </div>
        <!-- Конец Панель TABS -->
        
        </div>
        <!-- Конец Правый DIV раздел подробности -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->

        <!-- Центральный DIV -рабочая область -->
        <div data-options="region:'center',title:'Рабочая область - Группы. Пользователь: $formLogin'">

        <table id="dg" title="Группы" class="easyui-datagrid" style="width:100%;height:100%" toolbar="#tb, #toolbar" sortName="GROUP_NAME" sortOrder="asc" idField="ID"></table>
        <div id="toolbar">
        <a href="#" class="easyui-linkbutton" iconCls="icon-filter" plain="true" onclick="\$('#dlg_filter').window('open').dialog('center').dialog('setTitle','Фильтр')">Фильтр</a>
        <span id="lb" style="float:right; color: #F00; font-weight: bold;"></span>
        </div>

        <!-- Панель посика -->
        <div id="tb" style="padding:3px">
             <span>Поиск по наименованию группы:</span>
             <input id="group" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
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
    
    
    <!-- Форма установки фильтра группы -->    
    <div id="dlg_filter" class="easyui-dialog" style="width:350px;height:450px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Установка фильтра</div>
        <form id="fm_filter" novalidate>
            <table>
                <tr>
                    <td><label><input id="radio_LANGUAGE" name="radio" type="radio" value="0" />Курс:</label></td>
                    <td><input id="LANGUAGE" name="LANGUAGE" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_languages.cgi?SID=$SID', method: 'get'"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_LEVEL_KNOWLEDGE" name="radio" type="radio" value="1" />Уровень:</label></td>
                    <td><input id="LEVEL_KNOWLEDGE" name="LEVEL_KNOWLEDGE" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', valueText: 'text', url: 'get_level_knowledge.cgi?SID=$SID', method: 'get'"></input></td>
                </tr>
                <tr>
                    <td><label><input id="radio_KIND_PROGRAMM" name="radio" type="radio" value="2" />Программа:</label></td>
                    <td><input id="KIND_PROGRAMM" name="KIND_PROGRAMM" class="easyui-combobox" data-options="editable:false, panelHeight:'300px', valueField: 'id', valueText: 'text', groupField:'group', url: 'get_kind_prog.cgi?SID=$SID', method: 'get'"></input></td>
                </tr>                
                <tr>
                    <td><label><input id="radio_GROUP_TYPE" name="radio" type="radio" value="3" />Тип группы:</label></td>
                    <td><input id="GROUP_TYPE1" name="GROUP_TYPE" style="width:150px;"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_TYPE_CALC_LESSON" name="radio" type="radio" value="4" />Тип подсчета занятия:</label></td>
                    <td><input id="TYPE_CALC_LESSON" name="TYPE_CALC_LESSON" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', valueText: 'text', url: 'get_type_calc_lessons.cgi?SID=$SID', method: 'get'"></input></td>
                </tr>
                <tr>
                    <td><label><input id="radio_COUNT_CLASSES" name="radio" type="radio" value="5" />Кол-во занятий:</label></td>
                    <td><input id="COUNT_CLASSES" name="COUNT_CLASSES" class="easyui-numberbox"></td>
                </tr>
                 <tr>
                    <td><label><input id="radio_DURATION_CLASSES" name="radio" type="radio" value="6" />Продолжит. занятий:</label></td>
                    <td><input id="DURATION_CLASSES" name="DURATION_CLASSES" class="easyui-numberbox"></td>
                </tr>                
                <tr>
                    <td><label><input id="radio_COURSE_PRICE" name="radio" type="radio" value="7" />Цена курса:</label></td>
                    <td><input id="COURSE_PRICE" name="COURSE_PRICE" class="easyui-numberbox"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_TYPE_PAY" name="radio" type="radio" value="8" />Вид расчета:</label></td>
                    <td><input id="TYPE_PAY" name="TYPE_PAY" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', valueText: 'text', url: 'get_type_pay.cgi?SID=$SID', method: 'get'"></input></td>
                </tr>
                <tr>
                    <td><label><input id="radio_BRANCH" name="radio" type="radio" value="10" />Филиал:</label></td>
                    <td><input id="BRANCH" name="BRANCH" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', valueText: 'text', url: 'get_branches.cgi?SID=$SID', method: 'get'"></input></td>
                </tr>  
                <tr>
                    <td><label><input id="radio_ROOM" name="radio" type="radio" value="11" />Аудитория:</label></td>
                    <td><input id="ROOM_filter" name="ROOM_filter" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', valueText: 'text', url: 'get_room_4_lessons.cgi?SID=$SID', method: 'get'"></input></td>
                </tr>                     
                <tr>
                    <td><label><input id="radio_erase_filter" name="radio" type="radio" value="9" /><strong>Снять фильтры:</strong></label></td>                    
                </tr>
            </table>    
        </form>
    </div>
    <div id="dlg-buttons">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="doFilter()" style="width:100px">Установить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_filter').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма установки фильтра группы -->
    
    <!-- Форма добавления новой темы и ДЗ -->    
    <div id="dlg_topic_homework" class="easyui-dialog" style="width:520px;height:350px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons_topic_homework" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Информация о теме и ДЗ</div>
        <form id="fm_topic_homework" novalidate>
            <div class="fitem">
               	<label>Дата занятия:</label>
               	<input name="DATE_LESSON" class="easyui-datebox" data-options="required:true, formatter:myformatter, parser:myparser" missingMessage="Данное поле необходимо заполнить">
	        </div>
            <div class="fitem">
               	<label>Тема:</label>
               	<input name="TOPIC" class="easyui-textbox">
           	</div>
            <div class="fitem">
               	<label>ДЗ:</label>
               	<input name="HOME_WORK" class="easyui-textbox" data-options="multiline:true" style="height:100px">
	        </div>
            <div class="fitem">
			    <label></label>
                <a href="#" class="easyui-linkbutton" iconCls="icon-list" onclick="" style="">Привязать файл</a>			
			</div>
        </form>
    </div>
    <div id="dlg-buttons_topic_homework">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="saveTopic()" style="width:100px">Сохранить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_topic_homework').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма добавления новой темы и ДЗ -->
	
	   
    
       
        </body>
        </html>
HTML_e

     #Продлеваем время жизни сессии
     $sess->atime(time());
     $sess->flush();

  
   
#Удаление сессии
sub f_delete_session {
         #Удаляем куки
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://teachers.localhost:6080');
         print "Set-Cookie: $cookies\n";
         #Удаляем сессию
         $sess->delete();
         $sess->flush();
        }

#Добавление SID к URL-адресу
sub f_add_sid {
        my $url=shift();
        if ($method eq 'path') {
                if (defined($SID) && $url !~ m/SID=/) {
                        if ($url !~ m/\?/) {
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
else { print "Location: http://teachers.localhost:6080\n\n"; }