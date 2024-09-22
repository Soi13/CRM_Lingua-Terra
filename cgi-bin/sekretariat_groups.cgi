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
my $GROUPS_SEKRETARIAT=$sess->param('GROUPS_SEKRETARIAT');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

     if ($GROUPS_SEKRETARIAT==1) #Смотрим имеет ли доступ пользователь к модулю "Группы".
     {
        my $name_gr=param('name_gr'); #Если данная страница открыта как по щелчку по группе в студентах, то передается ID группы, чтобы знать на какую группу вставать  

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
       //group: \$('#group').val()
	   group: \$('#group').textbox('getText')
       });
       }
       </script>

       <script>
       \$(function(){
       \$('#dg').datagrid({
       onSelect:function(index){
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

       //Загружаем и выводим список привязанных студентов к группе
       \$('#list_of_students').datagrid({
       method:'get',
       showHeader: true,
       showFooter: true,
       scrollbarSize: 0,
       striped: true,
       border: false,
       singleSelect: true,
       url:'get_students_in_group.cgi?id_z1='+row.ID+'&SID=$SID',
       columns:[[
                          {field:'ID',title:'ID', hidden:true},
						  {field:'Num_dogovor',title:'Num_dogovor', hidden:true},
                          {field:'FIO',title:'<b>ФИО</b>'},
						  {field:'BEGIN_STUDY',title:'<b>Начало обучения</b>'},
                          {field:'name'},
                          {field:'count'}                 
                       ]]
                        });
       ////////////////////////////////////////////////////////////

      //Загружаем и выводим список занятий группы
       \$('#list_of_lessons').datagrid({
       title: 'Существующие занятия в группе',
       method:'get',
       showHeader: true,       
       scrollbarSize: 0,
       striped: true,
       border: false,
       singleSelect: true,
       url:'get_lessons_in_group.cgi?id_z2='+row.ID+'&SID=$SID',
       columns:[[
                 {field:'ID',title:'ID', hidden:true},
                 {field:'FIO',title:'<b>Преподаватель</b>'},
                 {field:'ROOM',title:'<b>Аудитория</b>'}                                  
               ]]
       });       
       //////////////////////////////////////////
       
       //Обновление календаря при перемещении по группам. Загрузка записей выделенной группы       
	scheduler.clearAll();
	scheduler.load("get_calendar_lessons_groups.cgi?SID=$SID"+"&id_gr="+row.ID,"json");		
	scheduler.updateView();     
        ///////////////////////////////////////////////////////////////////
        
        
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


       //Грузим вывод контекстной менюхи для установки даты начала обучения
       \$('#list_of_students').datagrid('getPanel').panel('panel').attr('tabindex',0).bind('contextmenu',function(e){
               e.preventDefault();
               \$('#mm_dt').menu('show', {
                   left: e.pageX,
                   top: e.pageY
               });
        });
        ////////////////////////////////////////////      	   

                                }
                        });
                });
        </script>
        
        <script type="text/javascript">
        var url;
        function newGroup(){
            \$('#dlg').dialog('open').dialog('center').dialog('setTitle','Новая группа');
            \$('#fm').form('clear');
            \$('#ts').timespinner('setValue', '00:00');  // set timespinner value
            \$('#COURSE_PRICE').numberbox('setValue', '0.00');
             url = 'insert_group.cgi?SID=$SID';
        }
        function editGroup(){
            var row = \$('#dg').datagrid('getSelected');
            if (row){
	        \$('#dlg').dialog('open').dialog('center').dialog('setTitle','Редактирование группы');
            \$('#fm').form('load',row);               
            url = 'edit_group.cgi?id_x='+row.ID+'&SID=$SID';      
            \$('#chd_gr_nm').val('');                                    
            }
        }
        
        function saveGroup() {
		var msg   = \$('#fm').serialize();
        \$.ajax({
          type: 'GET',
          url: url,
          data: msg,
          success: function(res) { \$.messager.alert('Информация',res.result,'info'); if (res.result=="Группа добавлена успешно!") {\$('#fm').form('clear'); \$('#dlg').dialog('close'); \$('#dg').datagrid('reload');} if (res.result=="Группа отредактирована успешно!") {\$('#fm').form('clear'); \$('#dlg').dialog('close'); \$('#dg').datagrid('reload');}},          error: function() {alert("did not work");}
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
		scheduler.load("get_calendar_events_students.cgi?SID=$SID","json");	
        	 
                                     scheduler.templates.event_bar_date = function(start,end,ev){
                                     return "• <b>"+scheduler.templates.event_date(start)+" - "+scheduler.templates.event_date(end)+"</b> ";
                                     };
		
	}
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
             course_price: \$('#COURSE_PRICE_FILTER').val()
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

      <script>//Установка фильтра для формы выбора студента при привязке его к группе
       function doFilter_4_tie_student(){
       
       //Проверка, выбран хотя бы один параметр фильтрации
       if((!\$("#radio_DATE_OF_DOGOVOR").prop("checked")) && (!\$("#radio_KIND_PROG").prop("checked")) && (!\$("#radio_erase_filter_tie").prop("checked"))) {
	    \$.messager.alert('Внимание','Не выбран параметр фильтрации!','warning');
	    return;
        }        
               
       ///////////////////
       if(\$("#radio_DATE_OF_DOGOVOR").prop("checked")) { 
              \$('#dg_add_student').datagrid('load',{
              date_of_dogovor_from: \$('#DATE_OF_DOGOVOR_FROM').datebox('getValue'),
              date_of_dogovor_to: \$('#DATE_OF_DOGOVOR_TO').datebox('getValue')             
              });
              \$('#lb_tie').text('Установлен фильтр по "Дата договора"');
       }
       ///////////////////
	   
	   ///////////////////
       if(\$("#radio_KIND_PROG").prop("checked")) { 
              \$('#dg_add_student').datagrid('load',{
              kind_prog: \$('#KIND_PROG').combobox('getValue'),
              });
              \$('#lb_tie').text('Установлен фильтр по "Программа"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_erase_filter_tie").prop("checked")) { 
              \$('#dg_add_student').datagrid('load',{
              erase_filter: 'switch_filter'
              });
              \$('#lb_tie').text('');
       }
       ///////////////////
 
       \$('#fm_filter_4_tie_student').form('clear'); \$('#dlg_filter_4_tie_student').dialog('close'); //Закрываем и форму фильтрации и очищаем поля
 
       }
       </script>//Конец скрипта установки фильтра для формы выбора студента при привязке его к группе
               
               
        <script> 
        \$(function(){
        \$('#cnt_lesson').combobox({
	onSelect: function(res){ 
	                          var rr=\$('#cnt_lesson').combobox('getValue');	                      
	                          if (rr==3) 
	                          {	                          
	                            \$('#cnt_class, #dur_class').hide();
	                            \$('#end_dt').show();
	                          }
	                          if (rr==2) 
	                          {
	                            \$('#cnt_class, #st_dt').show();
	                            \$('#end_dt, #dur_class').hide();
	                          }
	                          if (rr==1) 
	                          {
	                            \$('#cnt_class, #st_dt, #dur_class').show();
	                            \$('#end_dt').hide();
	                          }                       
	                       }
	        })        
            
         })
        </script>

        <script>
        \$(function(){
         \$('#gr_name').textbox({
	  onChange: function(res){
          \$('#chd_gr_nm').val('1');          
                                 }
            })
         })
        </script>

        <script>
        function open_window_add_stud(){
        var row_stud = \$('#dg').datagrid('getSelected');        
            if (row_stud){
            \$('#dlg_add_student').window('open').dialog('center').dialog('setTitle','Привязка студентов к группе');
            \$('#dg_add_student').datagrid({url: 'get_students_4_add_2_group.cgi?SID=$SID&br='+row_stud.BRANCH+'&gr='+row_stud.ID});
            }
        }
        </script>
                
        <script>
        function add_stud_2_group(){
        var row_stud = \$('#dg').datagrid('getSelected');        
            if (row_stud){            
            var ss = [];
            var rows = \$('#dg_add_student').datagrid('getSelections');
            ss.push(row_stud.ID);
            for(var i=0; i<rows.length; i++){
                var row = rows[i];
                ss.push(row.Num_dogovor);
            }     
            
            \$.ajax({            
            type: 'GET',
            traditional: true,
            url: 'add_students_2_group.cgi?SID=$SID',
            data: {'dat':ss},            
            success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result=="Студенты привязаны удачно!" || res.result=="Студент привязан удачно!") {\$('#dlg_add_student').dialog('close'); \$('#list_of_students').datagrid('reload');}},
            error: function() {alert("did not work");}
            });            
                         }
        }
        </script>
        
       <script> //Вывод кол-ва выделенных студентов
       \$(function(){
       \$('#dg_add_student').datagrid({
       onSelect:function(index){
                                 var rows = \$('#dg_add_student').datagrid('getSelections');
                                 \$('#lb_stud').text('Кол-во выбранных студентов:'+rows.length);        
                                },
       onUnselect:function(index){
                                 var rows = \$('#dg_add_student').datagrid('getSelections');
                                 \$('#lb_stud').text('Кол-во выбранных студентов:'+rows.length);        
                                },
       onSelectAll:function(index){
                                 var rows = \$('#dg_add_student').datagrid('getSelections');
                                 \$('#lb_stud').text('Кол-во выбранных студентов:'+rows.length);        
                                },
       onUnselectAll:function(index){
                                 var rows = \$('#dg_add_student').datagrid('getSelections');
                                 \$('#lb_stud').text('Кол-во выбранных студентов:'+rows.length);        
                                }
                        });
                });
        </script>

       <script>
        function open_window_create_lessons(){
        var row_less = \$('#dg').datagrid('getSelected');        
            if (row_less){             
            \$('#fm_lessons').form('clear');
            \$('.inputs').empty();
            \$('#dlg_create_lessons').window('open').dialog('center').dialog('setTitle','Создание занятий в группе');
            \$('#id_gr').val(row_less.ID);            
            }
        }
        </script>
        
        <script> //Динамическое добавление полей для ввода инфы по дням занятий и времени
        \$(function(){
             
             var i=0;
             //Добавление            
            \$('html').on('click','.add',function () {            
            var ff =\$('<div>    <div class="fitem">  <div class="fitem"><label>День недели:</label> <select name="DAYS" class="easyui-combobox" style="width:264px;" data-options="editable:false"><option value="1">Понедельник</option><option value="2">Вторник</option><option value="3">Среда</option><option value="4">Четверг</option><option value="5">Пятница</option><option value="6">Суббота</option><option value="0">Воскресенье</option></select></div>   <div class="fitem"><label>Время занятий</label>  C: &nbsp <input name="DAYS" class="easyui-timespinner" data-options="showSeconds:false" style="width:80px;"> По: &nbsp <input name="DAYS" class="easyui-timespinner" data-options="showSeconds:false" style="width:80px;"> </div>    <span class="remove"><a href="#">Удалить</a></span> <hr />  </div>').fadeIn('slow').appendTo('.inputs');
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
        
        <script>
        function add_lesson(){
        var msg   = \$('#fm_lessons').serialize();
        \$.ajax({
                  type: 'GET',
                  url: 'insert_lessons.cgi?SID=$SID',
                  data: msg,
                  success: function(res) { \$.messager.alert('Информация',res.result,'info'); if (res.result=="Занятия добавлены успешно!") {\$('#fm_lessons').form('clear'); \$('#dlg_create_lessons').dialog('close'); \$('#dg').datagrid('reload');} },          error: function() {alert("did not work");}
                });                   
        }
        </script>
        
       <script>//Функция выделения цветом 
       \$(function(){
       
       \$('#list_of_lessons').datagrid({
	rowStyler: function(index,row){
			return 'background-color:#e5caf2;'; // return inline style
			              }
        });
        
        \$('#list_of_periods_of_lessons').datagrid({
	rowStyler: function(index,row){
			return 'background-color:#e5f1ff;'; // return inline style
			          }
        });
		
		\$('#dg').datagrid({
	    rowStyler: function(index,row){
		if (row.DEBTS_STUDENT==1){
			return 'background-color:red;color:#fff;';				
		              }
	    }
        });
        
        });
        </script>
		
		 <script>
        function open_window_edit_lessons(){
        var row = \$('#dg').datagrid('getSelected');
        if (row){
	    \$('#dlg_edit_lessons').dialog('open').dialog('center').dialog('setTitle','Редактирование расписания');
	    \$('.edits').empty();
		\$('#var1').hide();
		startLoadingAnimation();
            
            \$('#TEACHER_ID_ED').combobox({
                               method: 'get',
                               editable: false,
                               required: true,
                               panelHeight: 'auto',
                               url:'get_teacher_4_lessons.cgi?SID=$SID',
                               valueField:'id',
                               textField:'text'
                              });  
            
            \$('#ROOM_ID_ED').combobox({
                               method: 'get',
                               editable: false,
                               required: true,
                               panelHeight: 'auto',
                               url:'get_room_4_lessons.cgi?SID=$SID',
                               valueField:'id',
                               textField:'text'
                              }); 
            
            \$.ajax({
            type: 'GET',
            url: 'get_lessons_4_edit.cgi?SID=$SID',
            cache: false,
            data: { 'id': row.ID },
            success: function(res1) {                                          
                                      for (var j=0; j<=res1.length-3; j++) 
                                      {                                               
                                       var rr = \$('<div>    <div class="fitem"> <input name="LESSONS_4_EDIT" value="' + res1[j].DATE_LESSON + '" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser" style="width:100px;"> <input name="LESSONS_4_EDIT" value="'+ res1[j].TIME_BEGIN +'" class="tm_beg easyui-timespinner" data-options="showSeconds:false" style="width:80px;">  <input name="LESSONS_4_EDIT" value="'+ res1[j].TIME_END +'" class="tm_end easyui-timespinner" data-options="showSeconds:false" style="width:80px;"> <input type="hidden" name="LESSONS_4_EDIT" value="' + res1[j].ID + '"> </div>  </div>').fadeIn('slow').appendTo('.edits'); 
                                        
                                       \$.parser.parse(rr);                                                                                                                   
                                      }
                                      \$('#TEACHER_ID_ED').combobox('setValue', res1[res1.length-2]);
                                      \$('#ROOM_ID_ED').combobox('setValue', res1[res1.length-1]);
									  stopLoadingAnimation();
                                     },
            error: function() {alert("did not work");}
            });                           
            \$('#idd_gr').val(row.ID);
            \$('#start_date').val(row.START_DATE);
            \$('#end_date').val(row.END_DATE);
            \$('#SID').val('$SID');            
            }
        }
        </script>
        
        <script>
        function edit_lessons() {
        var msg   = \$('#fm_lessons_edit').serialize();
        \$.ajax({
          type: 'POST',
          url: 'edit_lesson.cgi',
          data: msg,
          success: function(res) { \$.messager.alert('Информация',res.result,'info'); if (res.result=="Занятия отредактированы успешно!") {\$('#fm_lessons_edit').form('clear'); \$('#dlg_edit_lessons').dialog('close'); \$('#list_of_periods_of_lessons').datagrid('reload');}},          error: function() {alert("did not work");}
        });        
       }
       </script>
	   
	   <script> 
        \$(function(){
        \$('#GROUP_TYPE').combogrid({
         panelWidth:560,
         required: true,
         editable: false,
         idField:'id',
         textField:'text',
         method: 'get',
         url:'get_groups_list.cgi?SID=$SID',
         columns:[[
        {field:'id',title:'ID',width:60, hidden:true},
        {field:'text',title:'Тип группы',width:150},
        {field:'PRICE',title:'Цена',width:80},        
        {field:'TYPE_OPL',title:'Вид оплаты',width:120},
        {field:'DURATION',title:'Длительность',width:200}
         ]]
                           });

        
        \$('#GROUP_TYPE1').combogrid({
         panelWidth:560,
         editable: false,
         idField:'id',
         textField:'text',
         method: 'get',
         url:'get_groups_list.cgi?SID=$SID',
         columns:[[
        {field:'id',title:'ID',width:60, hidden:true},
        {field:'text',title:'Тип группы',width:150},
        {field:'PRICE',title:'Цена',width:80},        
        {field:'TYPE_OPL',title:'Вид оплаты',width:120},
        {field:'DURATION',title:'Длительность',width:200}
         ]]
                           });


            
            })
        </script>
		
		<script>
        function change_time() {
		if ((\$('#time_begin').val()=='') ||  (\$('#time_end').val()==''))
        { 
          \$.messager.alert('Внимание', 'Не все поля заполнены!','warning');
   		  return;
        }
		
		//Проверяем, чтобы время начала не было больше времени окончания занятий
        var date1 =  new Date();
        date1 = date1.setHours.apply(date1, \$('#time_begin').val().split(":"));
        var date2 =  new Date();
        date2 = date2.setHours.apply(date2, \$('#time_end').val().split(":"));
        //var diff = date2 - date1;
        if (date1>=date2) 
        {
          \$.messager.alert('Внимание', 'Время начала звнятий не может быть больше или равно времени окончания занятий!','warning');
           return;
        }
		
        \$('.tm_beg').timespinner('setValue', \$('#time_begin').val());
        \$('.tm_end').timespinner('setValue', \$('#time_end').val());                
        //Очищаем поля после редактирования
        \$('#time_begin').timespinner('setValue', '');
        \$('#time_end').timespinner('setValue', '');        
        \$('#var1').hide();
        }
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
		
		<script> //Функция удаления группы
        function delGroup(){
            var row = \$('#dg').datagrid('getSelected');
            if (row){
                \$.messager.confirm('Внимание','Вы уверены, что необходимо удалить выбранную группу?',function(r){
                    if (r){
                            \$.ajax({            
                            type: 'GET',
                            traditional: true,
                            url: 'delGroup.cgi?SID=$SID',
                            data: {'id_gr':row.ID},            
                            success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result=="Группа удалена успешно!") {\$('#dg').datagrid('reload');}},
                            error: function() {alert("did not work");}
                            });                       
                  
                          }
                });
            }
        }  
        </script>
		
		<script> //Функция удаления студента из группы
        function del_stud(){
            var row = \$('#list_of_students').datagrid('getSelected');
            if (row){
                \$.messager.confirm('Внимание','Вы уверены, что необходимо отвязать выбранного студента?',function(r){
                    if (r){
                            \$.ajax({            
                            type: 'GET',
                            traditional: true,
                            url: 'del_stud_from_group.cgi?SID=$SID',
                            data: {'id_stud':row.ID},            
                            success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result=="Студент отвязан успешно!") {\$('#list_of_students').datagrid('reload');}},
                            error: function() {alert("did not work");}
                            });                       
                  
                          }
                });
            }
        }  
        </script>
		
		<script> //Функция удаления расписания из группы
         function del_lessons(){
            var row = \$('#dg').datagrid('getSelected');
            if (row){
                \$.messager.confirm('Внимание','Вы уверены, что необходимо удалить занятия у данной группы?',function(r){
                    if (r){
                            \$.ajax({            
                            type: 'GET',
                            traditional: true,
                            url: 'del_lessons_from_group.cgi?SID=$SID',
                            data: {'id_group':row.ID},            
                            success: function(res) {\$.messager.alert('Информация',res.result,'info'); if (res.result=="Занятия удалены успешно!") {\$('#list_of_lessons, #list_of_periods_of_lessons').datagrid('reload');}},
                            error: function() {alert("did not work");}
                            });                       
                  
                          }
                });
            }
        }  
        </script>
		
		 <script>
        function open_window_set_date(){
            var row = \$('#list_of_students').datagrid('getSelected');            
            if (row){             
	    \$('#dlg_dt_beg').dialog('open').dialog('center').dialog('setTitle','Установка даты начала обучения');
            \$('#id_st').val(row.ID);            
            }
        }
        </script>
		
		<script>
        function set_date_study() {
        var msg   = \$('#fm_dt_beg').serialize();
        \$.ajax({
          type: 'GET',
          url: 'set_date_study.cgi?SID=$SID',
          data: msg,
          success: function(res) { \$.messager.alert('Информация',res.result,'info'); if (res.result=="Дата установлена успешно!") {\$('#fm_dt_beg').form('clear'); \$('#dlg_dt_beg').dialog('close'); \$('#list_of_students').datagrid('reload');}},          error: function() {alert("did not work");}
        });        
       }
       </script>
	   
	   <script>
       \$(function(){
       \$('#list_of_students').datagrid({
        onDblClickRow:function(index, row){
                                             window.location.href = "sekretariat_students.cgi?SID=$SID&nm_dog="+row.Num_dogovor;        
                                          }
                           
                        });
                });
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
        function find_group(){ 
       	 var myId1 = $name_gr;
       	 var p_size=\$('#dg').datagrid('options').pageSize;

       	 \$.ajax({            
            type: 'GET',
            traditional: true,
            url: 'get_page_group.cgi?SID=$SID',
            data: {'nm_gr':myId1, 'page_size':p_size},            
            success: function(res) {      
            	                     \$('#dg').datagrid('gotoPage', {
                                               page: res.result,
                                                callback: function(){
                                               index = \$('#dg').datagrid('getRowIndex', myId1);
                                               if (index >= 0){
                                                                 setTimeout(function(){
                                                                                           \$('#dg').datagrid('selectRow', index);
                                                                                      },0)
                                                              }
                                                                   }
                                              
                                         
                                                                     });
                                                                     
                                           
            	                        
            	                   },
            error: function() { alert("did not work"); }
            }); 
       	 
        }
        </script>
    
        </head>
HTML
      
	    if (defined($name_gr))
        {
            print qq(<body class="easyui-layout" onload="init(); setTimeout('find_group()',1000)">);
        }
        else
        {
            print qq(<body class="easyui-layout" onload="init();">);
        } 
 
        print <<HTML2;
        <!--Верхний DIV - заголовок -->
        <div data-options="region:'north',border:false" style="height:100px;background:#f0993c;padding:10px;"><h1 class="shd">@name_org</h1>
        <!--DIV В котором лежат кнопки панели-->
HTML2

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
         <div title="Студенты">
            <!--Кнопка привязки студента к группе -->
            <div style="padding:10px 10px;">
            <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-add'" onclick="open_window_add_stud()">Привязать студента</a>
			<a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-remove'" onclick="del_stud()">Отвязать студента</a>
            </div>
            <!--Конец Кнопка привязки студента к группе -->

            <!-- Вывод списка привязанных студентов к группе -->
            <table id="list_of_students"></table>
            <!-- Конец Вывод списка привязанных студентов к группе -->

         </div>
         <div title="Генератор занятий">

            <!--Кнопка создания и редактирования занятий в группе -->
            <div style="padding:10px 10px;">
            <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-add'" onclick="open_window_create_lessons()">Создать занятия</a>
			<a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-edit'" onclick="open_window_edit_lessons()">Редактировать занятия</a>
			<a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-remove'" onclick="del_lessons()">Удалить занятия</a>
            </div>
            <!--Конец Кнопка создания и редактирования занятий в группе -->
            
            <!-- Вывод занятий группы -->
            <table id="list_of_lessons"></table>
            <!-- Конец Вывод занятий группы -->
            
            <!-- Вывод списка времени и дат занятий группы -->
            <table id="list_of_periods_of_lessons"></table>
            <!-- Конец Вывод списка времени и дат занятий группы -->

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
               </div>
               <div class="dhx_cal_header"></div>
               <div class="dhx_cal_data"></div>
           </div>        
           <!-- Конец Календарь -->         

         </div>
         <div title="Конфликты">
         </div>
         <div title="Посещаемость">
         </div>         
        </div>
        <!-- Конец Панель TABS -->
        
        </div>
        <!-- Конец Правый DIV раздел подробности -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->

        <!-- Центральный DIV -рабочая область -->
        <div data-options="region:'center',title:'Рабочая область - Группы. Пользователь: $formLogin'">

        <table id="dg" title="Группы" class="easyui-datagrid" style="width:100%;height:100%"
        method="get"
        url="get_groups.cgi?SID=$SID"
        toolbar="#tb, #toolbar"
        rownumbers="true" fitColumns="true" singleSelect="true" pagination="true" sortName="GROUP_NAME" sortOrder="asc" idField="ID" striped=true>

        <thead>
        <tr>
            <th field="ID" width="15" sortable="true" hidden="true">ID1</th>
            <th field="GROUP_NAME" width="150" sortable="true">Наименование группы</th>
            <th field="START_DATE" width="60" sortable="true">Дата начала</th>
            <th field="END_DATE" width="60" sortable="true">Дата окончания</th>
            <th field="COURSE_PRICE" width="25" sortable="true">Цена курса</th>                        
        </tr>
        </thead>
        </table>
        <div id="toolbar">
        <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="newGroup()">Добавить группу</a>
        <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="editGroup()">Редактировать группу</a>
		<a href="#" class="easyui-linkbutton" iconCls="icon-remove" plain="true" onclick="delGroup()">Удалить группу</a>
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
    
    <!-- Форма добавления новой группы -->    
    <div id="dlg" class="easyui-dialog" style="width:500px;height:620px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Информация о группе</div>
        <form id="fm" novalidate>
            <div class="fitem">
               	<label>Курс:</label>
               	<input name="LANGUAGE" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_languages.cgi?SID=$SID', method: 'get'" missingMessage="Данное поле необходимо заполнить">
           	</div>
            <div class="fitem">
               	<label>Уровень:</label>
               	<input name="LEVEL_KNOWLEDGE" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_level_knowledge.cgi?SID=$SID', method: 'get'">
           	</div>
           <div class="fitem">
               	<label>Программа:</label>
               	<input name="KIND_PROGRAMM" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'300px', valueField: 'id', textField: 'text', groupField:'group', url: 'get_kind_prog.cgi?SID=$SID', method: 'get'" missingMessage="Данное поле необходимо заполнить">
           	</div>
            <div class="fitem">
               	<label>Наименование группы:</label>
               	<input id="gr_name" name="GROUP_NAME" class="easyui-textbox" required missingMessage="Данное поле необходимо заполнить">
	        </div>
            <div class="fitem">
               	<label>Тип группы:</label>
               	<input name="GROUP_TYPE" id="GROUP_TYPE">
           	</div> 
            <div class="fitem">
               	<label>Посчитать занятия:</label>
               	<input id="cnt_lesson" name="TYPE_CALC_LESSON" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_type_calc_lessons.cgi?SID=$SID', method: 'get'" missingMessage="Данное поле необходимо заполнить">
           	</div>
            <div class="fitem" id="cnt_class">
               	<label>Кол-во занятий:</label>
               	<input name="COUNT_CLASSES" class="easyui-numberbox">
	        </div> 
            <div class="fitem" id="dur_class">
               	<label>Продолжит. занятий:</label>
               	<input name="DURATION_CLASSES" class="easyui-numberbox">
	        </div>
            <div class="fitem" id="st_dt">
               	<label>Дата начала:</label>
               	<input name="START_DATE" class="easyui-datebox" data-options="required:true, formatter:myformatter, parser:myparser" missingMessage="Данное поле необходимо заполнить">
	        </div>
            <div class="fitem" id="end_dt">
               	<label>Дата окончания:</label>
               	<input id="end_dt" name="END_DATE" class="easyui-datebox" data-options="required:true, formatter:myformatter, parser:myparser" missingMessage="Данное поле необходимо заполнить">
	        </div>
            <div class="fitem">
               	<label>Цена курса (&#8381;):</label>
               	<input id="COURSE_PRICE" name="COURSE_PRICE" class="easyui-numberbox" data-options="precision:2">
	        </div>
            <div class="fitem">
               	<label>Минимальное кол-во студентов:</label>
               	<input name="MIN_COUNT_STUDENTS" class="easyui-numberbox">
	        </div>
            <div class="fitem">
               	<label>Максимальное кол-во студентов:</label>
               	<input name="MAX_COUNT_STUDENTS" class="easyui-numberbox">
	        </div>
            <div class="fitem">
               	<label>Вид расчета:</label>
               	<input name="TYPE_PAY" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_type_pay.cgi?SID=$SID', method: 'get'" missingMessage="Данное поле необходимо заполнить">
           	</div>
            <div class="fitem">
               	<label>Филиал:</label>
               	<input name="BRANCH" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_branches.cgi?SID=$SID', method: 'get'" missingMessage="Данное поле необходимо заполнить">
           	</div>
            <div class="fitem">
               	<label>Организация/Фирма:</label>
               	<input name="FIRM" class="easyui-combobox">
           	</div>

                  <input name="chd_gr_nm" type="hidden" id="chd_gr_nm" value="" />
        </form>
    </div>
    <div id="dlg-buttons">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="saveGroup()" style="width:100px">Сохранить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма добавления новой группы -->
    
    
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
                    <td><input id="COURSE_PRICE_FILTER" name="COURSE_PRICE_FILTER" class="easyui-numberbox"></td>
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

    <!-- Форма привязки студента к группе -->    
    <div id="dlg_add_student" class="easyui-dialog" style="width:370px;height:500px;padding:10px 5px 0px 5px;"
            closed="true" modal="true" buttons="#dlg-buttons_stud" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <span id="lb_stud" style="float:left; font-weight: bold; margin-bottom:10px;">Кол-во выбранных студентов:</span>
        <table id="dg_add_student" class="easyui-datagrid" style="width:100%;height:75%"
        method="get" rownumbers="true" fitColumns="true" sortName="FIO" sortOrder="asc" striped=true>

        <thead>
        <tr>
            <th field="ck_bx" checkbox="true"></th>
            <th field="Num_dogovor" width="15" sortable="true" hidden="true">Num_dogovor</th>
            <th field="FIO" width="70" sortable="true">ФИО</th>
            <th field="DATE_OF_BORN" width="60" sortable="true">Дата рождения</th>                                    
        </tr>
        </thead>
        </table>
        <!--Кнопка фильтра -->
            <div style="padding:10px 10px;">
            <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-filter'" onclick="\$('#dlg_filter_4_tie_student').window('open').dialog('center').dialog('setTitle','Фильтр')">Фильтр</a>
            </div>
        <!--Конец Кнопка фильтра -->
        <span id="lb_tie" style="float:right; color: #F00; font-weight: bold;"></span>
    </div> 
    <div id="dlg-buttons_stud">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="add_stud_2_group()" style="width:100px">Привязать</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_add_student').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма привязки студента к группе -->

    <!-- Форма создания занятий для группы -->    
    <div id="dlg_create_lessons" class="easyui-dialog" style="width:500px;height:570px;padding:10px 1px;"
            closed="true" modal="true" buttons="#dlg-buttons_create_lessons" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Информация о занятиях</div>
        <form id="fm_lessons" novalidate>
            <div class="fitem">
               	<label>Преподаватель:</label>
               	<input name="TEACHER_ID" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_teacher_4_lessons.cgi?SID=$SID', method: 'get'" missingMessage="Данное поле необходимо заполнить">
           	</div>
            <div class="fitem">
               	<label>Кабинет/Аудитория:</label>
               	<input name="ROOM_ID" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_room_4_lessons.cgi?SID=$SID', method: 'get'" missingMessage="Данное поле необходимо заполнить">
           	</div> 
            <div class="fitem ad">
               	<label><b>Информация о днях и времени занятий.</b></label>
                </div>	
	    <div class="fitem ad">
                <span class="addField add">
                <a href="#" id="add" class="easyui-linkbutton" data-options="iconCls:'icon-add'">Добавить</a>
                </span>               
               	</div>	 
               	<!-- Добавление инфы о днях и времени  -->
                <div class="inputs">               
                </div>
                <!-- Конец Добавление инфы о днях и времени -->
                
                <input name="id_gr" type="hidden" id="id_gr" value="" />
           
        </form>
    </div>
    <div id="dlg-buttons_create_lessons">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="add_lesson()" style="width:100px">Сохранить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_create_lessons').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма создания занятий для группы -->

    <!-- Форма установки фильтра при выборе студента для привязки к группе -->    
    <div id="dlg_filter_4_tie_student" class="easyui-dialog" style="width:500px;height:220px;padding:10px 1px;"
            closed="true" modal="true" buttons="#dlg-buttons_4_tie_student" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Установка фильтра</div>
        <form id="fm_filter_4_tie_student" novalidate>
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
    <div id="dlg-buttons_4_tie_student">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="doFilter_4_tie_student()" style="width:100px">Установить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_filter_4_tie_student').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма установки фильтра при выборе студента для привязки к группе -->
	
	<!-- Форма редактирования занятий для группы -->    
    <div id="dlg_edit_lessons" class="easyui-dialog" style="width:370px;height:570px;padding:10px 1px;"
            closed="true" modal="true" buttons="#dlg-buttons_edit_lessons" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Информация о занятиях</div>
        <form id="fm_lessons_edit" novalidate>                    
            <div class="fitem">
               	<label>Преподаватель:</label>
               	<input id="TEACHER_ID_ED" name="TEACHER_ID_ED">
           	</div>
            <div class="fitem">
               	<label>Кабинет/Аудитория:</label>
               	<input id="ROOM_ID_ED" name="ROOM_ID_ED">
           	</div> 
			<div class="fitem">
           	<a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-add'" onclick="javascript: \$('#var1').show();">Групповое изменение времени</a>
                </div> 
            <!-- Блок ввода информации о групповом редактировании времени.-->
            <div  id="var1" style="display: none;">            
               <label><b>Групповое редактирование времени.</b></label>
            <div class="fitem">
               <label>Время:</label>
               </div>
            <div class="fitem">
               С: <input name="time_begin" id="time_begin" class="easyui-timespinner" data-options="showSeconds:false" style="width:80px;">  По: <input name="time_end" id="time_end" class="easyui-timespinner" data-options="showSeconds:false" style="width:80px;">               
	           </div>
	        <div class="fitem">	        
           	   <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-add'" onclick="change_time()">Подтвердить</a>           	
                </div> 	                   
                <hr>
           </div>
           <!-- Конец Блок ввода информации о групповом редактировании времени. -->
                <!-- Поля для редактирования расписания-->
                <div class="edits">               
                </div>
                <!-- Конец Поля для редактирования расписания -->
                
                <input name="idd_gr" type="hidden" id="idd_gr" value="" />
                <input name="start_date" type="hidden" id="start_date" value="" />
                <input name="end_date" type="hidden" id="end_date" value="" />
				<input name="SID" type="hidden" id="SID" value="" />
        </form>
    </div>
    <div id="dlg-buttons_edit_lessons">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="edit_lessons()" style="width:100px">Сохранить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_edit_lessons').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма редактирования занятий для группы -->
	
	<!-- Вывод картинки лоадера -->
    <img id="loadImg" src="../images/loader.gif" /> 
	
	<!--Контекстное меню -->
    <div id="mm_dt" class="easyui-menu" style="width:290px;">
        <div data-options="iconCls:'icon-tip'" onclick="open_window_set_date();"><strong>Установить дату начала обучения</strong></div>        
    </div>
    <!--Конец Контекстное меню -->
    
    <!-- Форма установки даты начала обучения студента -->    
    <div id="dlg_dt_beg" class="easyui-dialog" style="width:330px;height:200px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">Установка даты:</div>
        <form id="fm_dt_beg" novalidate>           
            <div class="fitem">
               	<label>Дата начала обучения:</label>
               	<input name="DATE_ST_BEG" class="easyui-datebox" data-options="required:true, formatter:myformatter, parser:myparser" missingMessage="Данное поле необходимо заполнить">
	        </div>
                           
                <input id="id_st" name="id_st" type="hidden" value="" />
                           	
        </form>
    </div>
    <div id="dlg-buttons">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="set_date_study()" style="width:100px">Установить</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_dt_beg').dialog('close')" style="width:90px">Отменить</a>
    </div>
    <!-- Конец Форма установки даты начала обучения студента -->
       
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