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

#���� ������ ������
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#���� ����� ������ �������
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#���� IP �� ���������
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#����������� ���������� ����� � ������ ������������ �� ������
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $GROUPS_SEKRETARIAT=$sess->param('GROUPS_SEKRETARIAT');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

     if ($GROUPS_SEKRETARIAT==1) #������� ����� �� ������ ������������ � ������ "������".
     {
        my $name_gr=param('name_gr'); #���� ������ �������� ������� ��� �� ������ �� ������ � ���������, �� ���������� ID ������, ����� ����� �� ����� ������ ��������  

        #���������� �������� ����������� ��� ������ �� �� ��������
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
        \$.messager.confirm('��������', '�� �������, ��� ���������� �����', function(r){
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

        <script> //�������� ����� ����� ������
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
       //��������� � ��������� ����������� �� �������
       \$('#pg').propertygrid({
       method:'get',
       url: 'get_groups_detail.cgi?id_z='+row.ID+'&SID=$SID',
       showGroup: true,
       showHeader: false,
       scrollbarSize: 0
       });
       //////////////////////////////////////////

       //��������� � ������� ������ ����������� ��������� � ������
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
                          {field:'FIO',title:'<b>���</b>'},
						  {field:'BEGIN_STUDY',title:'<b>������ ��������</b>'},
                          {field:'name'},
                          {field:'count'}                 
                       ]]
                        });
       ////////////////////////////////////////////////////////////

      //��������� � ������� ������ ������� ������
       \$('#list_of_lessons').datagrid({
       title: '������������ ������� � ������',
       method:'get',
       showHeader: true,       
       scrollbarSize: 0,
       striped: true,
       border: false,
       singleSelect: true,
       url:'get_lessons_in_group.cgi?id_z2='+row.ID+'&SID=$SID',
       columns:[[
                 {field:'ID',title:'ID', hidden:true},
                 {field:'FIO',title:'<b>�������������</b>'},
                 {field:'ROOM',title:'<b>���������</b>'}                                  
               ]]
       });       
       //////////////////////////////////////////
       
       //���������� ��������� ��� ����������� �� �������. �������� ������� ���������� ������       
	scheduler.clearAll();
	scheduler.load("get_calendar_lessons_groups.cgi?SID=$SID"+"&id_gr="+row.ID,"json");		
	scheduler.updateView();     
        ///////////////////////////////////////////////////////////////////
        
        
        //��������� � ������� ������ ������� � ��� ������� ������
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
                 {field:'WEEK_DAY',title:'<b>���� ������</b>'},
                 {field:'DATE_LESSON',title:'<b>���� �������</b>'},
                 {field:'TIME_BEGIN',title:'<b>����� ������</b>'},
                 {field:'TIME_END',title:'<b>����� ���������</b>'}                                  
               ]]
       });       
       //////////////////////////////////////////   


       //������ ����� ����������� ������ ��� ��������� ���� ������ ��������
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
            \$('#dlg').dialog('open').dialog('center').dialog('setTitle','����� ������');
            \$('#fm').form('clear');
            \$('#ts').timespinner('setValue', '00:00');  // set timespinner value
            \$('#COURSE_PRICE').numberbox('setValue', '0.00');
             url = 'insert_group.cgi?SID=$SID';
        }
        function editGroup(){
            var row = \$('#dg').datagrid('getSelected');
            if (row){
	        \$('#dlg').dialog('open').dialog('center').dialog('setTitle','�������������� ������');
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
          success: function(res) { \$.messager.alert('����������',res.result,'info'); if (res.result=="������ ��������� �������!") {\$('#fm').form('clear'); \$('#dlg').dialog('close'); \$('#dg').datagrid('reload');} if (res.result=="������ ��������������� �������!") {\$('#fm').form('clear'); \$('#dlg').dialog('close'); \$('#dg').datagrid('reload');}},          error: function() {alert("did not work");}
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
   
       
        <script>//��������� Keyboard Navigation
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
       
       <script type="text/javascript"> //���������� ���������
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
				{name:"�������� �������", height:130, map_to:"text", type:"textarea" , focus:true},
				{name:"�����������", height:43, type:"textarea", map_to:"details" },
				{name:"time", height:72, type:"time", map_to:"auto"}
			];
	
		scheduler.init('scheduler_here',new Date(),"month");
		scheduler.setLoadMode("month");
		scheduler.load("get_calendar_events_students.cgi?SID=$SID","json");	
        	 
                                     scheduler.templates.event_bar_date = function(start,end,ev){
                                     return "� <b>"+scheduler.templates.event_date(start)+" - "+scheduler.templates.event_date(end)+"</b> ";
                                     };
		
	}
        </script>
       
             
       <script>//��������� �������
       function doFilter(){
       
       //��������, ������ ���� �� ���� �������� ����������
       if((!\$("#radio_LANGUAGE").prop("checked")) && (!\$("#radio_LEVEL_KNOWLEDGE").prop("checked")) && (!\$("#radio_GROUP_TYPE").prop("checked")) && (!\$("#radio_TYPE_CALC_LESSON").prop("checked")) && (!\$("#radio_COUNT_CLASSES").prop("checked")) && (!\$("#radio_DURATION_CLASSES").prop("checked")) && (!\$("#radio_COURSE_PRICE").prop("checked")) && (!\$("#radio_TYPE_PAY").prop("checked")) && (!\$("#radio_KIND_PROGRAMM").prop("checked")) && (!\$("#radio_BRANCH").prop("checked")) && (!\$("#radio_ROOM").prop("checked")) && (!\$("#radio_erase_filter").prop("checked"))) {
	    \$.messager.alert('��������','�� ������ �������� ����������!','warning');
	    return;
        }        
               
       ///////////////////
       if(\$("#radio_LANGUAGE").prop("checked")) { 
              \$('#dg').datagrid('load',{
             language: \$('#LANGUAGE').combobox('getValue')                                          
              });
              \$('#lb').text('���������� ������ �� "����"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_LEVEL_KNOWLEDGE").prop("checked")) { 
              \$('#dg').datagrid('load',{
             level_knowledge: \$('#LEVEL_KNOWLEDGE').combobox('getValue')
              });
              \$('#lb').text('���������� ������ �� "�������"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_KIND_PROGRAMM").prop("checked")) { 
              \$('#dg').datagrid('load',{
             kind_programm: \$('#KIND_PROGRAMM').combobox('getValue')
              });
              \$('#lb').text('���������� ������ �� "���������"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_GROUP_TYPE").prop("checked")) { 
              \$('#dg').datagrid('load',{
             group_type: \$('#GROUP_TYPE').combobox('getValue')
              });
              \$('#lb').text('���������� ������ �� "��� ������"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_TYPE_CALC_LESSON").prop("checked")) { 
              \$('#dg').datagrid('load',{
             type_calc_lesson: \$('#TYPE_CALC_LESSON').combobox('getValue')
              });
              \$('#lb').text('���������� ������ �� "������ ������� �������"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_COUNT_CLASSES").prop("checked")) { 
              \$('#dg').datagrid('load',{
             count_classes: \$('#COUNT_CLASSES').val()
              });
              \$('#lb').text('���������� ������ �� "���-�� �������"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_DURATION_CLASSES").prop("checked")) { 
              \$('#dg').datagrid('load',{
             duration_classes: \$('#DURATION_CLASSES').val()
              });
              \$('#lb').text('���������� ������ �� "����������������� �������"');
       }
       ///////////////////
                            
       ///////////////////
       if(\$("#radio_COURSE_PRICE").prop("checked")) { 
              \$('#dg').datagrid('load',{
             course_price: \$('#COURSE_PRICE_FILTER').val()
              });
              \$('#lb').text('���������� ������ �� "���� �����"');
       }
       ///////////////////
                    
       ///////////////////
       if(\$("#radio_TYPE_PAY").prop("checked")) { 
              \$('#dg').datagrid('load',{
             type_pay: \$('#TYPE_PAY').combobox('getValue')
              });
              \$('#lb').text('���������� ������ �� "��� �������"');
       }
       ///////////////////

       ///////////////////
       if(\$("#radio_BRANCH").prop("checked")) { 
              \$('#dg').datagrid('load',{
             branch: \$('#BRANCH').combobox('getValue')
              });
              \$('#lb').text('���������� ������ �� "������"');
       }
       ///////////////////
	   
	   ///////////////////
       if(\$("#radio_ROOM").prop("checked")) { 
              \$('#dg').datagrid('load',{
             room: \$('#ROOM_filter').combobox('getValue')
              });
              \$('#lb').text('���������� ������ �� "���������"');
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
 
       \$('#fm_filter').form('clear'); \$('#dlg_filter').dialog('close'); //��������� � ����� ���������� � ������� ����
 
       }
       </script>//����� ������� ��������� �������

      <script>//��������� ������� ��� ����� ������ �������� ��� �������� ��� � ������
       function doFilter_4_tie_student(){
       
       //��������, ������ ���� �� ���� �������� ����������
       if((!\$("#radio_DATE_OF_DOGOVOR").prop("checked")) && (!\$("#radio_KIND_PROG").prop("checked")) && (!\$("#radio_erase_filter_tie").prop("checked"))) {
	    \$.messager.alert('��������','�� ������ �������� ����������!','warning');
	    return;
        }        
               
       ///////////////////
       if(\$("#radio_DATE_OF_DOGOVOR").prop("checked")) { 
              \$('#dg_add_student').datagrid('load',{
              date_of_dogovor_from: \$('#DATE_OF_DOGOVOR_FROM').datebox('getValue'),
              date_of_dogovor_to: \$('#DATE_OF_DOGOVOR_TO').datebox('getValue')             
              });
              \$('#lb_tie').text('���������� ������ �� "���� ��������"');
       }
       ///////////////////
	   
	   ///////////////////
       if(\$("#radio_KIND_PROG").prop("checked")) { 
              \$('#dg_add_student').datagrid('load',{
              kind_prog: \$('#KIND_PROG').combobox('getValue'),
              });
              \$('#lb_tie').text('���������� ������ �� "���������"');
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
 
       \$('#fm_filter_4_tie_student').form('clear'); \$('#dlg_filter_4_tie_student').dialog('close'); //��������� � ����� ���������� � ������� ����
 
       }
       </script>//����� ������� ��������� ������� ��� ����� ������ �������� ��� �������� ��� � ������
               
               
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
            \$('#dlg_add_student').window('open').dialog('center').dialog('setTitle','�������� ��������� � ������');
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
            success: function(res) {\$.messager.alert('����������',res.result,'info'); if (res.result=="�������� ��������� ������!" || res.result=="������� �������� ������!") {\$('#dlg_add_student').dialog('close'); \$('#list_of_students').datagrid('reload');}},
            error: function() {alert("did not work");}
            });            
                         }
        }
        </script>
        
       <script> //����� ���-�� ���������� ���������
       \$(function(){
       \$('#dg_add_student').datagrid({
       onSelect:function(index){
                                 var rows = \$('#dg_add_student').datagrid('getSelections');
                                 \$('#lb_stud').text('���-�� ��������� ���������:'+rows.length);        
                                },
       onUnselect:function(index){
                                 var rows = \$('#dg_add_student').datagrid('getSelections');
                                 \$('#lb_stud').text('���-�� ��������� ���������:'+rows.length);        
                                },
       onSelectAll:function(index){
                                 var rows = \$('#dg_add_student').datagrid('getSelections');
                                 \$('#lb_stud').text('���-�� ��������� ���������:'+rows.length);        
                                },
       onUnselectAll:function(index){
                                 var rows = \$('#dg_add_student').datagrid('getSelections');
                                 \$('#lb_stud').text('���-�� ��������� ���������:'+rows.length);        
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
            \$('#dlg_create_lessons').window('open').dialog('center').dialog('setTitle','�������� ������� � ������');
            \$('#id_gr').val(row_less.ID);            
            }
        }
        </script>
        
        <script> //������������ ���������� ����� ��� ����� ���� �� ���� ������� � �������
        \$(function(){
             
             var i=0;
             //����������            
            \$('html').on('click','.add',function () {            
            var ff =\$('<div>    <div class="fitem">  <div class="fitem"><label>���� ������:</label> <select name="DAYS" class="easyui-combobox" style="width:264px;" data-options="editable:false"><option value="1">�����������</option><option value="2">�������</option><option value="3">�����</option><option value="4">�������</option><option value="5">�������</option><option value="6">�������</option><option value="0">�����������</option></select></div>   <div class="fitem"><label>����� �������</label>  C: &nbsp <input name="DAYS" class="easyui-timespinner" data-options="showSeconds:false" style="width:80px;"> ��: &nbsp <input name="DAYS" class="easyui-timespinner" data-options="showSeconds:false" style="width:80px;"> </div>    <span class="remove"><a href="#">�������</a></span> <hr />  </div>').fadeIn('slow').appendTo('.inputs');
            \$.parser.parse(ff);
            i++;
            if (i>0) {\$('#add').linkbutton({iconCls: 'icon-add', text: '�������� ���'});}
            });
            
            //��������
            \$('html').on('click','.remove', function () {                               
            \$(this).parent().remove();
            i--;
            if (i<1) {\$('#add').linkbutton({iconCls: 'icon-add', text: '��������'});}
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
                  success: function(res) { \$.messager.alert('����������',res.result,'info'); if (res.result=="������� ��������� �������!") {\$('#fm_lessons').form('clear'); \$('#dlg_create_lessons').dialog('close'); \$('#dg').datagrid('reload');} },          error: function() {alert("did not work");}
                });                   
        }
        </script>
        
       <script>//������� ��������� ������ 
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
	    \$('#dlg_edit_lessons').dialog('open').dialog('center').dialog('setTitle','�������������� ����������');
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
          success: function(res) { \$.messager.alert('����������',res.result,'info'); if (res.result=="������� ��������������� �������!") {\$('#fm_lessons_edit').form('clear'); \$('#dlg_edit_lessons').dialog('close'); \$('#list_of_periods_of_lessons').datagrid('reload');}},          error: function() {alert("did not work");}
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
        {field:'text',title:'��� ������',width:150},
        {field:'PRICE',title:'����',width:80},        
        {field:'TYPE_OPL',title:'��� ������',width:120},
        {field:'DURATION',title:'������������',width:200}
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
        {field:'text',title:'��� ������',width:150},
        {field:'PRICE',title:'����',width:80},        
        {field:'TYPE_OPL',title:'��� ������',width:120},
        {field:'DURATION',title:'������������',width:200}
         ]]
                           });


            
            })
        </script>
		
		<script>
        function change_time() {
		if ((\$('#time_begin').val()=='') ||  (\$('#time_end').val()==''))
        { 
          \$.messager.alert('��������', '�� ��� ���� ���������!','warning');
   		  return;
        }
		
		//���������, ����� ����� ������ �� ���� ������ ������� ��������� �������
        var date1 =  new Date();
        date1 = date1.setHours.apply(date1, \$('#time_begin').val().split(":"));
        var date2 =  new Date();
        date2 = date2.setHours.apply(date2, \$('#time_end').val().split(":"));
        //var diff = date2 - date1;
        if (date1>=date2) 
        {
          \$.messager.alert('��������', '����� ������ ������� �� ����� ���� ������ ��� ����� ������� ��������� �������!','warning');
           return;
        }
		
        \$('.tm_beg').timespinner('setValue', \$('#time_begin').val());
        \$('.tm_end').timespinner('setValue', \$('#time_end').val());                
        //������� ���� ����� ��������������
        \$('#time_begin').timespinner('setValue', '');
        \$('#time_end').timespinner('setValue', '');        
        \$('#var1').hide();
        }
        </script>
		
		 <script>
        function startLoadingAnimation() // - ������� ������� ��������
        {
          // ������ ������� � ������������ �������� � ������ �����������:
          var imgObj = \$('#loadImg');
          imgObj.show();
 
          // �������� � ����� ���������� ����� ��������� ����������� ��������,
          // ����� ��� ��������� � �������� ��������:
          var centerY = \$(window).scrollTop() + (\$(window).height() + imgObj.height())/2;
          var centerX = \$(window).scrollLeft() + (\$(window).width() + imgObj.width())/2;
 
          // �������� ���������� ����������� �� ������:
          imgObj.offset({top:centerY, left:centerX});
        }
 
        function stopLoadingAnimation() // - ������� ��������������� ��������
        {
           \$('#loadImg').hide();
        }        
        </script>
		
		<script> //����������� ������ �� ������� Enter
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
		
		<script> //������� �������� ������
        function delGroup(){
            var row = \$('#dg').datagrid('getSelected');
            if (row){
                \$.messager.confirm('��������','�� �������, ��� ���������� ������� ��������� ������?',function(r){
                    if (r){
                            \$.ajax({            
                            type: 'GET',
                            traditional: true,
                            url: 'delGroup.cgi?SID=$SID',
                            data: {'id_gr':row.ID},            
                            success: function(res) {\$.messager.alert('����������',res.result,'info'); if (res.result=="������ ������� �������!") {\$('#dg').datagrid('reload');}},
                            error: function() {alert("did not work");}
                            });                       
                  
                          }
                });
            }
        }  
        </script>
		
		<script> //������� �������� �������� �� ������
        function del_stud(){
            var row = \$('#list_of_students').datagrid('getSelected');
            if (row){
                \$.messager.confirm('��������','�� �������, ��� ���������� �������� ���������� ��������?',function(r){
                    if (r){
                            \$.ajax({            
                            type: 'GET',
                            traditional: true,
                            url: 'del_stud_from_group.cgi?SID=$SID',
                            data: {'id_stud':row.ID},            
                            success: function(res) {\$.messager.alert('����������',res.result,'info'); if (res.result=="������� ������� �������!") {\$('#list_of_students').datagrid('reload');}},
                            error: function() {alert("did not work");}
                            });                       
                  
                          }
                });
            }
        }  
        </script>
		
		<script> //������� �������� ���������� �� ������
         function del_lessons(){
            var row = \$('#dg').datagrid('getSelected');
            if (row){
                \$.messager.confirm('��������','�� �������, ��� ���������� ������� ������� � ������ ������?',function(r){
                    if (r){
                            \$.ajax({            
                            type: 'GET',
                            traditional: true,
                            url: 'del_lessons_from_group.cgi?SID=$SID',
                            data: {'id_group':row.ID},            
                            success: function(res) {\$.messager.alert('����������',res.result,'info'); if (res.result=="������� ������� �������!") {\$('#list_of_lessons, #list_of_periods_of_lessons').datagrid('reload');}},
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
	    \$('#dlg_dt_beg').dialog('open').dialog('center').dialog('setTitle','��������� ���� ������ ��������');
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
          success: function(res) { \$.messager.alert('����������',res.result,'info'); if (res.result=="���� ����������� �������!") {\$('#fm_dt_beg').form('clear'); \$('#dlg_dt_beg').dialog('close'); \$('#list_of_students').datagrid('reload');}},          error: function() {alert("did not work");}
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
        //���������� ���� TextBox ������� KeyUp ��� ������ �� ����
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
        <!--������� DIV - ��������� -->
        <div data-options="region:'north',border:false" style="height:100px;background:#f0993c;padding:10px;"><h1 class="shd">@name_org</h1>
        <!--DIV � ������� ����� ������ ������-->
HTML2

        #���������� ������, ������� ����� �� ������� ������
        open FF1, "<txt_data/buttons_panel.txt";
        my @buttons_panel=<FF1>;
        foreach my $str_but (@buttons_panel)
        {
           $str_but=~s/\0//g;
           $str_but=~s/\.\.//g;
           $str_but=~s/[<]*script[^>]*>.*[<]*\/script[>]*//i; #�� ���� ������ ������� ���� <script>
		   $str_but=~s/SID=\$SID/SID=$SID/i; #����������� ���������� ���� SID � ������ ������ ���������� $SID. ��� �� �� �������������, �.�. ������ �������� �� ���������� �����.
        }
        close (FF1) or die $!;        
        print @buttons_panel;
        #########################################
        
        print <<HTML1; 
        <!--����� DIV � ������� ����� ������ ������-->
        </div>
        <!--����� ������� DIV - ��������� -->

        <!--����� DIV ������ ���� -->
        <div data-options="region:'west',split:false,title:'����'" style="width:205px;">

        <div id='cssmenu'>
        <ul>
HTML1
        #���������� � ��������� ����
        my $us_id=$sess->param('USER_ID'); #������ �� ������ USER_ID
        Build_Menu->menu($us_id, $SID); #� �������� ������� ��������� ID ������������ ��� ������ ����
        print <<HTML_e;
        </ul>
        </div>

        </div>
        <!--����� ����� DIV ������ ���� -->

        <!-- ������ DIV ������ ����������� -->
        <div data-options="region:'east',split:true,title:'�����������'" style="width:30%;padding:1px;">
        
         <!--������ TABS -->
        <div class="easyui-tabs" style="width:100%; height:auto;" data-options="narrow:true, fit:true">
         <div title="�����">
         <table id="pg" style="width:100%"></table>
         </div>
         <div title="��������">
            <!--������ �������� �������� � ������ -->
            <div style="padding:10px 10px;">
            <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-add'" onclick="open_window_add_stud()">��������� ��������</a>
			<a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-remove'" onclick="del_stud()">�������� ��������</a>
            </div>
            <!--����� ������ �������� �������� � ������ -->

            <!-- ����� ������ ����������� ��������� � ������ -->
            <table id="list_of_students"></table>
            <!-- ����� ����� ������ ����������� ��������� � ������ -->

         </div>
         <div title="��������� �������">

            <!--������ �������� � �������������� ������� � ������ -->
            <div style="padding:10px 10px;">
            <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-add'" onclick="open_window_create_lessons()">������� �������</a>
			<a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-edit'" onclick="open_window_edit_lessons()">������������� �������</a>
			<a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-remove'" onclick="del_lessons()">������� �������</a>
            </div>
            <!--����� ������ �������� � �������������� ������� � ������ -->
            
            <!-- ����� ������� ������ -->
            <table id="list_of_lessons"></table>
            <!-- ����� ����� ������� ������ -->
            
            <!-- ����� ������ ������� � ��� ������� ������ -->
            <table id="list_of_periods_of_lessons"></table>
            <!-- ����� ����� ������ ������� � ��� ������� ������ -->

         </div>         
         <div title="���������">
         
           <!-- ��������� -->
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
           <!-- ����� ��������� -->         

         </div>
         <div title="���������">
         </div>
         <div title="������������">
         </div>         
        </div>
        <!-- ����� ������ TABS -->
        
        </div>
        <!-- ����� ������ DIV ������ ����������� -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->

        <!-- ����������� DIV -������� ������� -->
        <div data-options="region:'center',title:'������� ������� - ������. ������������: $formLogin'">

        <table id="dg" title="������" class="easyui-datagrid" style="width:100%;height:100%"
        method="get"
        url="get_groups.cgi?SID=$SID"
        toolbar="#tb, #toolbar"
        rownumbers="true" fitColumns="true" singleSelect="true" pagination="true" sortName="GROUP_NAME" sortOrder="asc" idField="ID" striped=true>

        <thead>
        <tr>
            <th field="ID" width="15" sortable="true" hidden="true">ID1</th>
            <th field="GROUP_NAME" width="150" sortable="true">������������ ������</th>
            <th field="START_DATE" width="60" sortable="true">���� ������</th>
            <th field="END_DATE" width="60" sortable="true">���� ���������</th>
            <th field="COURSE_PRICE" width="25" sortable="true">���� �����</th>                        
        </tr>
        </thead>
        </table>
        <div id="toolbar">
        <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="newGroup()">�������� ������</a>
        <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="editGroup()">������������� ������</a>
		<a href="#" class="easyui-linkbutton" iconCls="icon-remove" plain="true" onclick="delGroup()">������� ������</a>
        <a href="#" class="easyui-linkbutton" iconCls="icon-filter" plain="true" onclick="\$('#dlg_filter').window('open').dialog('center').dialog('setTitle','������')">������</a>
        <span id="lb" style="float:right; color: #F00; font-weight: bold;"></span>
        </div>

        <!-- ������ ������ -->
        <div id="tb" style="padding:3px">
             <span>����� �� ������������ ������:</span>
             <input id="group" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
             <a href="#" class="easyui-linkbutton" plain="false" onclick="doSearch()" style="border-radius:5px; width:100px;">������</a>
        </div>
        <!-- ����� ������ ��� ������ -->

        </div>
        <!-- ����� ����������� DIV -������� ������� -->

        <!-- ����� ��������� ������ -->
        <div id="w" class="easyui-window" title="����� ������" data-options="modal:true,closed:true,iconCls:'icon-save'" style="width:370px;height:170px;padding:10px;">
        <form id="ff" action="javascript:void(null);" onsubmit="call()" method="post" enctype="multipart/form-data">
            <table>
                <tr>
                    <td>������� ������:</td>
                    <td><input id="curr_psw" name="curr_psw" type="password" class="f1 easyui-textbox"></input></td>
                </tr>
                <tr>
                    <td>����� ������:</td>
                    <td><input name="new_psw" type="password" class="f1 easyui-textbox"></input></td>
                </tr>
                <tr>
                    <td>��� ���:</td>
                    <td><input name="new_psw1" type="password" class="f1 easyui-textbox"></input></td>
                </tr>
                <tr>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                </tr>
                <tr>
                    <td></td>
                    <td><input type="submit" value="�����������"></input></td>
                </tr>
            </table>
        </form>
    </div>
    <!-- ����� ����� ��������� ������ -->
    
    <!-- ����� ���������� ����� ������ -->    
    <div id="dlg" class="easyui-dialog" style="width:500px;height:620px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">���������� � ������</div>
        <form id="fm" novalidate>
            <div class="fitem">
               	<label>����:</label>
               	<input name="LANGUAGE" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_languages.cgi?SID=$SID', method: 'get'" missingMessage="������ ���� ���������� ���������">
           	</div>
            <div class="fitem">
               	<label>�������:</label>
               	<input name="LEVEL_KNOWLEDGE" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_level_knowledge.cgi?SID=$SID', method: 'get'">
           	</div>
           <div class="fitem">
               	<label>���������:</label>
               	<input name="KIND_PROGRAMM" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'300px', valueField: 'id', textField: 'text', groupField:'group', url: 'get_kind_prog.cgi?SID=$SID', method: 'get'" missingMessage="������ ���� ���������� ���������">
           	</div>
            <div class="fitem">
               	<label>������������ ������:</label>
               	<input id="gr_name" name="GROUP_NAME" class="easyui-textbox" required missingMessage="������ ���� ���������� ���������">
	        </div>
            <div class="fitem">
               	<label>��� ������:</label>
               	<input name="GROUP_TYPE" id="GROUP_TYPE">
           	</div> 
            <div class="fitem">
               	<label>��������� �������:</label>
               	<input id="cnt_lesson" name="TYPE_CALC_LESSON" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_type_calc_lessons.cgi?SID=$SID', method: 'get'" missingMessage="������ ���� ���������� ���������">
           	</div>
            <div class="fitem" id="cnt_class">
               	<label>���-�� �������:</label>
               	<input name="COUNT_CLASSES" class="easyui-numberbox">
	        </div> 
            <div class="fitem" id="dur_class">
               	<label>���������. �������:</label>
               	<input name="DURATION_CLASSES" class="easyui-numberbox">
	        </div>
            <div class="fitem" id="st_dt">
               	<label>���� ������:</label>
               	<input name="START_DATE" class="easyui-datebox" data-options="required:true, formatter:myformatter, parser:myparser" missingMessage="������ ���� ���������� ���������">
	        </div>
            <div class="fitem" id="end_dt">
               	<label>���� ���������:</label>
               	<input id="end_dt" name="END_DATE" class="easyui-datebox" data-options="required:true, formatter:myformatter, parser:myparser" missingMessage="������ ���� ���������� ���������">
	        </div>
            <div class="fitem">
               	<label>���� ����� (&#8381;):</label>
               	<input id="COURSE_PRICE" name="COURSE_PRICE" class="easyui-numberbox" data-options="precision:2">
	        </div>
            <div class="fitem">
               	<label>����������� ���-�� ���������:</label>
               	<input name="MIN_COUNT_STUDENTS" class="easyui-numberbox">
	        </div>
            <div class="fitem">
               	<label>������������ ���-�� ���������:</label>
               	<input name="MAX_COUNT_STUDENTS" class="easyui-numberbox">
	        </div>
            <div class="fitem">
               	<label>��� �������:</label>
               	<input name="TYPE_PAY" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_type_pay.cgi?SID=$SID', method: 'get'" missingMessage="������ ���� ���������� ���������">
           	</div>
            <div class="fitem">
               	<label>������:</label>
               	<input name="BRANCH" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_branches.cgi?SID=$SID', method: 'get'" missingMessage="������ ���� ���������� ���������">
           	</div>
            <div class="fitem">
               	<label>�����������/�����:</label>
               	<input name="FIRM" class="easyui-combobox">
           	</div>

                  <input name="chd_gr_nm" type="hidden" id="chd_gr_nm" value="" />
        </form>
    </div>
    <div id="dlg-buttons">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="saveGroup()" style="width:100px">���������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� ���������� ����� ������ -->
    
    
    <!-- ����� ��������� ������� ������ -->    
    <div id="dlg_filter" class="easyui-dialog" style="width:350px;height:450px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">��������� �������</div>
        <form id="fm_filter" novalidate>
            <table>
                <tr>
                    <td><label><input id="radio_LANGUAGE" name="radio" type="radio" value="0" />����:</label></td>
                    <td><input id="LANGUAGE" name="LANGUAGE" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_languages.cgi?SID=$SID', method: 'get'"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_LEVEL_KNOWLEDGE" name="radio" type="radio" value="1" />�������:</label></td>
                    <td><input id="LEVEL_KNOWLEDGE" name="LEVEL_KNOWLEDGE" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', valueText: 'text', url: 'get_level_knowledge.cgi?SID=$SID', method: 'get'"></input></td>
                </tr>
                <tr>
                    <td><label><input id="radio_KIND_PROGRAMM" name="radio" type="radio" value="2" />���������:</label></td>
                    <td><input id="KIND_PROGRAMM" name="KIND_PROGRAMM" class="easyui-combobox" data-options="editable:false, panelHeight:'300px', valueField: 'id', valueText: 'text', groupField:'group', url: 'get_kind_prog.cgi?SID=$SID', method: 'get'"></input></td>
                </tr>                
                <tr>
                    <td><label><input id="radio_GROUP_TYPE" name="radio" type="radio" value="3" />��� ������:</label></td>
                    <td><input id="GROUP_TYPE1" name="GROUP_TYPE" style="width:150px;"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_TYPE_CALC_LESSON" name="radio" type="radio" value="4" />��� �������� �������:</label></td>
                    <td><input id="TYPE_CALC_LESSON" name="TYPE_CALC_LESSON" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', valueText: 'text', url: 'get_type_calc_lessons.cgi?SID=$SID', method: 'get'"></input></td>
                </tr>
                <tr>
                    <td><label><input id="radio_COUNT_CLASSES" name="radio" type="radio" value="5" />���-�� �������:</label></td>
                    <td><input id="COUNT_CLASSES" name="COUNT_CLASSES" class="easyui-numberbox"></td>
                </tr>
                 <tr>
                    <td><label><input id="radio_DURATION_CLASSES" name="radio" type="radio" value="6" />���������. �������:</label></td>
                    <td><input id="DURATION_CLASSES" name="DURATION_CLASSES" class="easyui-numberbox"></td>
                </tr>                
                <tr>
                    <td><label><input id="radio_COURSE_PRICE" name="radio" type="radio" value="7" />���� �����:</label></td>
                    <td><input id="COURSE_PRICE_FILTER" name="COURSE_PRICE_FILTER" class="easyui-numberbox"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_TYPE_PAY" name="radio" type="radio" value="8" />��� �������:</label></td>
                    <td><input id="TYPE_PAY" name="TYPE_PAY" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', valueText: 'text', url: 'get_type_pay.cgi?SID=$SID', method: 'get'"></input></td>
                </tr>  
                <tr>
                    <td><label><input id="radio_BRANCH" name="radio" type="radio" value="10" />������:</label></td>
                    <td><input id="BRANCH" name="BRANCH" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', valueText: 'text', url: 'get_branches.cgi?SID=$SID', method: 'get'"></input></td>
                </tr> 
                <tr>
                    <td><label><input id="radio_ROOM" name="radio" type="radio" value="11" />���������:</label></td>
                    <td><input id="ROOM_filter" name="ROOM_filter" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', valueText: 'text', url: 'get_room_4_lessons.cgi?SID=$SID', method: 'get'"></input></td>
                </tr>				
                <tr>
                    <td><label><input id="radio_erase_filter" name="radio" type="radio" value="9" /><strong>����� �������:</strong></label></td>                    
                </tr>
            </table>    
        </form>
    </div>
    <div id="dlg-buttons">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="doFilter()" style="width:100px">����������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_filter').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� ��������� ������� ������ -->

    <!-- ����� �������� �������� � ������ -->    
    <div id="dlg_add_student" class="easyui-dialog" style="width:370px;height:500px;padding:10px 5px 0px 5px;"
            closed="true" modal="true" buttons="#dlg-buttons_stud" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <span id="lb_stud" style="float:left; font-weight: bold; margin-bottom:10px;">���-�� ��������� ���������:</span>
        <table id="dg_add_student" class="easyui-datagrid" style="width:100%;height:75%"
        method="get" rownumbers="true" fitColumns="true" sortName="FIO" sortOrder="asc" striped=true>

        <thead>
        <tr>
            <th field="ck_bx" checkbox="true"></th>
            <th field="Num_dogovor" width="15" sortable="true" hidden="true">Num_dogovor</th>
            <th field="FIO" width="70" sortable="true">���</th>
            <th field="DATE_OF_BORN" width="60" sortable="true">���� ��������</th>                                    
        </tr>
        </thead>
        </table>
        <!--������ ������� -->
            <div style="padding:10px 10px;">
            <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-filter'" onclick="\$('#dlg_filter_4_tie_student').window('open').dialog('center').dialog('setTitle','������')">������</a>
            </div>
        <!--����� ������ ������� -->
        <span id="lb_tie" style="float:right; color: #F00; font-weight: bold;"></span>
    </div> 
    <div id="dlg-buttons_stud">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="add_stud_2_group()" style="width:100px">���������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_add_student').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� �������� �������� � ������ -->

    <!-- ����� �������� ������� ��� ������ -->    
    <div id="dlg_create_lessons" class="easyui-dialog" style="width:500px;height:570px;padding:10px 1px;"
            closed="true" modal="true" buttons="#dlg-buttons_create_lessons" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">���������� � ��������</div>
        <form id="fm_lessons" novalidate>
            <div class="fitem">
               	<label>�������������:</label>
               	<input name="TEACHER_ID" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_teacher_4_lessons.cgi?SID=$SID', method: 'get'" missingMessage="������ ���� ���������� ���������">
           	</div>
            <div class="fitem">
               	<label>�������/���������:</label>
               	<input name="ROOM_ID" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_room_4_lessons.cgi?SID=$SID', method: 'get'" missingMessage="������ ���� ���������� ���������">
           	</div> 
            <div class="fitem ad">
               	<label><b>���������� � ���� � ������� �������.</b></label>
                </div>	
	    <div class="fitem ad">
                <span class="addField add">
                <a href="#" id="add" class="easyui-linkbutton" data-options="iconCls:'icon-add'">��������</a>
                </span>               
               	</div>	 
               	<!-- ���������� ���� � ���� � �������  -->
                <div class="inputs">               
                </div>
                <!-- ����� ���������� ���� � ���� � ������� -->
                
                <input name="id_gr" type="hidden" id="id_gr" value="" />
           
        </form>
    </div>
    <div id="dlg-buttons_create_lessons">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="add_lesson()" style="width:100px">���������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_create_lessons').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� �������� ������� ��� ������ -->

    <!-- ����� ��������� ������� ��� ������ �������� ��� �������� � ������ -->    
    <div id="dlg_filter_4_tie_student" class="easyui-dialog" style="width:500px;height:220px;padding:10px 1px;"
            closed="true" modal="true" buttons="#dlg-buttons_4_tie_student" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">��������� �������</div>
        <form id="fm_filter_4_tie_student" novalidate>
            <table>
                 <tr>
                    <td><label><input id="radio_DATE_OF_DOGOVOR" name="radio" type="radio" value="0" />���� ��������:    ��--</label></td>
                    <td><input id="DATE_OF_DOGOVOR_FROM" name="DATE_OF_DOGOVOR_FROM" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser">   ��--<input id="DATE_OF_DOGOVOR_TO" name="DATE_OF_DOGOVOR_TO" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser"></td>
                </tr>
                <tr>                    
                    <td><label><input id="radio_KIND_PROG" name="radio" type="radio" value="1" />���������:</label></td>
                    <td><input id="KIND_PROG" name="KIND_PROG" class="easyui-combobox" style="width:330px;" data-options="editable:false, panelHeight:'300px', valueField: 'id', valueText: 'text', groupField:'group', url: 'get_kind_prog.cgi?SID=$SID', method: 'get'"></input></td>
                </tr>				
                <tr>
                    <td><label><input id="radio_erase_filter_tie" name="radio" type="radio" value="9" /><strong>����� �������:</strong></label></td>                    
                </tr>
            </table>    
        </form>
    </div>
    <div id="dlg-buttons_4_tie_student">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="doFilter_4_tie_student()" style="width:100px">����������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_filter_4_tie_student').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� ��������� ������� ��� ������ �������� ��� �������� � ������ -->
	
	<!-- ����� �������������� ������� ��� ������ -->    
    <div id="dlg_edit_lessons" class="easyui-dialog" style="width:370px;height:570px;padding:10px 1px;"
            closed="true" modal="true" buttons="#dlg-buttons_edit_lessons" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">���������� � ��������</div>
        <form id="fm_lessons_edit" novalidate>                    
            <div class="fitem">
               	<label>�������������:</label>
               	<input id="TEACHER_ID_ED" name="TEACHER_ID_ED">
           	</div>
            <div class="fitem">
               	<label>�������/���������:</label>
               	<input id="ROOM_ID_ED" name="ROOM_ID_ED">
           	</div> 
			<div class="fitem">
           	<a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-add'" onclick="javascript: \$('#var1').show();">��������� ��������� �������</a>
                </div> 
            <!-- ���� ����� ���������� � ��������� �������������� �������.-->
            <div  id="var1" style="display: none;">            
               <label><b>��������� �������������� �������.</b></label>
            <div class="fitem">
               <label>�����:</label>
               </div>
            <div class="fitem">
               �: <input name="time_begin" id="time_begin" class="easyui-timespinner" data-options="showSeconds:false" style="width:80px;">  ��: <input name="time_end" id="time_end" class="easyui-timespinner" data-options="showSeconds:false" style="width:80px;">               
	           </div>
	        <div class="fitem">	        
           	   <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-add'" onclick="change_time()">�����������</a>           	
                </div> 	                   
                <hr>
           </div>
           <!-- ����� ���� ����� ���������� � ��������� �������������� �������. -->
                <!-- ���� ��� �������������� ����������-->
                <div class="edits">               
                </div>
                <!-- ����� ���� ��� �������������� ���������� -->
                
                <input name="idd_gr" type="hidden" id="idd_gr" value="" />
                <input name="start_date" type="hidden" id="start_date" value="" />
                <input name="end_date" type="hidden" id="end_date" value="" />
				<input name="SID" type="hidden" id="SID" value="" />
        </form>
    </div>
    <div id="dlg-buttons_edit_lessons">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="edit_lessons()" style="width:100px">���������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_edit_lessons').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� �������������� ������� ��� ������ -->
	
	<!-- ����� �������� ������� -->
    <img id="loadImg" src="../images/loader.gif" /> 
	
	<!--����������� ���� -->
    <div id="mm_dt" class="easyui-menu" style="width:290px;">
        <div data-options="iconCls:'icon-tip'" onclick="open_window_set_date();"><strong>���������� ���� ������ ��������</strong></div>        
    </div>
    <!--����� ����������� ���� -->
    
    <!-- ����� ��������� ���� ������ �������� �������� -->    
    <div id="dlg_dt_beg" class="easyui-dialog" style="width:330px;height:200px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">��������� ����:</div>
        <form id="fm_dt_beg" novalidate>           
            <div class="fitem">
               	<label>���� ������ ��������:</label>
               	<input name="DATE_ST_BEG" class="easyui-datebox" data-options="required:true, formatter:myformatter, parser:myparser" missingMessage="������ ���� ���������� ���������">
	        </div>
                           
                <input id="id_st" name="id_st" type="hidden" value="" />
                           	
        </form>
    </div>
    <div id="dlg-buttons">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="set_date_study()" style="width:100px">����������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_dt_beg').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� ��������� ���� ������ �������� �������� -->
       
        </body>
        </html>
HTML_e

        #���������� ����� ����� ������
        $sess->atime(time());
        $sess->flush();
  }
  else
  {
       &f_delete_session(); #������� ������
       
       print "Content-type: text/html\n\n";
       print <<HTML3;
       
       <!doctype html>
       <html>
       <head>
       <meta charset="windows-1251">
       <title>��� �������</title>

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
       <h1 align="center" class="zagolovok"><strong>� ��� ��� ������� � ������� ������!</strong></h1>
       </body>
       </html>       
HTML3
   }   

#�������� ������
sub f_delete_session {
         #������� ����
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://localhost:6080');
         print "Set-Cookie: $cookies\n";
         #������� ������
         $sess->delete();
         $sess->flush();
        }

#���������� SID � URL-������
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