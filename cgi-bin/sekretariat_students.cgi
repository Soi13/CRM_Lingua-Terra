#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
use CGI qw(:standart);
use CGI::Session;
use CGI qw(:cgi);
#use CGI::Carp qw (fatalsToBrowser);
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

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:spending",User=>"root", Password=>""}) or die  CGI::Session->errstr();
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

#���� IP- ������ �� ���������
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#����������� ���������� ����� � ������ ������������ �� ������
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $STUDENTS_SEKRETARIAT=$sess->param('STUDENTS_SEKRETARIAT');

#������� ����������� �� ����� � ������ ������������ � ������
if (defined($formLogin) && defined($formPass)) {

     if ($STUDENTS_SEKRETARIAT==1) #������� ����� �� ������ ������������ � ������ "��������".
     { 
        my $num_dog=param('nm_dog'); #���� ������ �������� ������� ��� �� ������ �� �������� � �������, �� ���������� ����� ��������, ����� ����� �� ������ �������� ��������
				
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
		<script type="text/javascript" src="../JS/datagrid-detailview.js"></script>
        <script src="../JS/script.js"></script>
        <script src="../ckeditor/ckeditor.js"></script>
        <script src="../ckeditor/adapters/jquery.js"></script> 

        <script>
        function confirm1(){
        \$.messager.confirm('��������!', '�� �������, ��� ���������� �����?', function(r){
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
                                });  });
       </script>


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
        //fio: \$('#fio').val(),
		fio: \$('#fio').textbox('getText'),
		//n_dogovor: \$('#n_dogovor').val()
		n_dogovor: \$('#n_dogovor').numberbox('getText'),
		fio_parent: \$('#fio_parent').textbox('getText')
        });
        }
        </script>

       <script>
       \$(function(){
       \$('#dg').datagrid({
       onSelect:function(index){
       var row = \$('#dg').datagrid('getSelected');
       //��������� � ��������� ����������� �� ��������
       \$('#pg').propertygrid({
       method:'get',
       url: 'get_student_detail.cgi?num_dog='+row.Num_dogovor+'&SID=$SID',
       showGroup: true,
       showHeader: false,
       scrollbarSize: 0,
	   nowrap: false
       });
       //////////////////////////////////////////

      //��������� � ��������� ������� �� ��������       
       \$('#hs').datagrid({
       method:'get',
       url:'get_student_history.cgi?num_dog='+row.Num_dogovor+'&SID=$SID',
       nowrap: false,
       fitColumns: true,
       singleSelect:true,
       columns:[[       
       {field:'DATETIME_CREATE',title:'���� �������'},
       {field:'TEXT',title:'����������'}
       ]]
       });
       //////////////////////////////////////////  

       //��������� � ������� ������ ����������� ���������� � ��������
       \$('#list_of_docum').datagrid({
       method:'get',
       showHeader: false,
       showFooter: true,
       scrollbarSize: 0,
       striped: true,
       border: false,
       singleSelect: true,
       url:'get_docum_in_student.cgi?id_z2='+row.Num_dogovor+'&SID=$SID',
       columns:[[
                 {field:'ID',title:'ID', hidden:true},
                 {field:'NAME_DOC',title:'��� ���������'},
                 {field:'DATE_START_DOGOVOR',title:'���� ��������'},
                 {field:'name',title:'name'},
                 {field:'count',title:'count'}
                 
               ]]
       });
       
       //////////////////////////////////////////

       //��������� � ������� ������ ����� � ������� �������� �������
       \$('#list_of_groups').datagrid({       
       title: '������������ ������ � ��������:',
       method:'get',
       showHeader: false,
       showFooter: false,
       scrollbarSize: 0,
       striped: true,
       border: false,
       singleSelect: true,
       url:'get_group_in_student.cgi?id_z3='+row.Num_dogovor+'&SID=$SID',
       columns:[[
	             {field:'GROUP_ID', hidden:true},
                 {field:'GROUP_NAME',title:'������������ ������'},                 
                 {field:'LANGUAGE',title:'����'},
                 {field:'NAME_PROGRAMM',title:'������������ ���������'}
                 //{field:'name',title:'name'},
                 //{field:'count',title:'count'}
                 
               ]]
       });       
       //////////////////////////////////////////

       //��������� � ������� ������ �������� ��� ��������
       \$('#list_of_pays').datagrid({       
       title: '�������:',
       method:'get',
       showHeader: true,
       showFooter: false,
       scrollbarSize: 0,
       striped: true,
       border: false,
       singleSelect: true,
       url:'get_pays_in_student.cgi?id_z4='+row.Num_dogovor+'&SID=$SID',
       columns:[[
                 {field:'ID',title:'ID', hidden: true},                 
                 {field:'PERIOD',title:'������'},
                 {field:'SUMM_4_OPL',title:'����� ��� ������'},
                 {field:'OPL_SUMM',title:'���������� �����'},
                 {field:'DATE_OF_PAY',title:'���� �������'},                 
                 {field:'STATUS',title:'������'}                                  
               ]]
       });       
       //////////////////////////////////////////
	   
	   //��������� ������������ ������ � ��������� �����
       //\$('#group').load('get_group_name.cgi?id_g='+row.Num_dogovor+'&SID=$SID');
             
               
         var ss = [];
         ss.push(row.Num_dogovor);
         \$.ajax({            
         type: 'GET',
         traditional: true,
         url: 'get_group_name.cgi?SID=$SID',
         data: {'data':ss},            
         success: function(res) {
                                  \$('#group').text('��.: '+res.result); //��������� ������������ � ��������� �����                                  
                                  \$('#p').show();
                                  \$('#p').progressbar({
                                                         value: res.proc
                                                      });
                                  \$('#paid').text('�������� ��������: '+res.summ_debt+' ���.'); //��������� ������������ � ��������� �����
                                  \$('#sum_debt').text(res.summ_debt_curr_per+' ���.'); 
								  \$('#debt_4_today').text('���� �� �������: '+res.summ_debt_curr_per+' ���.');
                                },
         error: function() {
                             \$('#group').text('');
                             \$('#p').hide();
                             \$('#paid').text('');  
                             \$('#sum_debt').text('');
                             \$('#debt_4_today').text('');
                           }
         
         
         });       
       ///////////////////////////////////////////////////////////////////////////
	   
	   
	   //��������� ������� ������������� ������� � ��������
       var conf = {            
            options:{
                fitColumns:true,
				showHeader:false,
				singleSelect: true,
                columns:[[                    
                    {field:'PERIOD',title:'������ ��������',width:200}                    
                ]],                
                method: 'get',
                url:'get_student_past_academ_period.cgi?SID=$SID&number_dog='+row.Num_dogovor,
            },
            subgrid:{
                options:{
				    title: '������ �� ������',
                    fitColumns:true,
                    nowrap:false,
                    foreignField:'uuid_main',
                    foreignField:function(prow){
				return {
					uuid_main: prow.UUID
			        	}				
			},                    
                    columns:[[
                        {field:'GROUP_NAME',title:'������',width:200},
                        {field:'LANGUAGE',title:'����',width:200},
                        {field:'PROGRAMM_NAME',title:'���������',width:200},
                        {field:'TEACHER_FIO',title:'�������������',width:200},
                        {field:'BRANCH',title:'������',width:200}
                    ]],
                    method: 'get',
                    url:'get_student_past_academ_period_gr.cgi?SID=$SID',
                },
                subgrid:{
                    options:{
					    title: '������� ��������',
                        fitColumns:true,
                        nowrap:false,
                        foreignField:'uuid_main1',
                        foreignField:function(prow){
				return {
					uuid_main1: prow.PAST_ACADEM_YEARS_UUID
				       }
				},
                        columns:[[
                            {field:'TYPE_DOC',title:'��� ���������',width:200,align:'right'},
                            {field:'COURSE',title:'���������',width:200,align:'right'},
                            {field:'TYPE_GROUP',title:'��� ������',width:200,align:'right'},
                            {field:'PRICE_COURSE',title:'���������',width:200,align:'right'},
                            {field:'DATE_START_DOGOVOR',title:'������ ��������',width:200,align:'right'},
                            {field:'DATE_END_DOGOVOR',title:'��������� ��������',width:200,align:'right'}
                        ]],
                        method: 'get',
                        url:'get_student_past_academ_period_doc.cgi?SID=$SID',
                    },
                    subgrid:{
                        options:{
						    title: '�������',
                            fitColumns:true,
                            nowrap:false,                          
                            foreignField:'uuid_main2',
                            foreignField:function(prow){
				return {
					uuid_main2: prow.PAST_ACADEM_YEARS_UUID
				       }
				},
                            singleSelect:true,
                            columns:[[
                                {field:'PERIOD',title:'������',width:200,align:'right'},
                                {field:'SUMM_4_OPL',title:'����� ��� ������',width:200,align:'right'},
                                {field:'OPL_SUMM',title:'���������� �����',width:200,align:'right'},
                                {field:'DATE_OF_PAY',title:'���� �������',width:200,align:'right'},
                                {field:'STATUS',title:'������',width:200,align:'right'}
                            ]],
                            method: 'get',
                            url:'get_student_past_academ_period_pays.cgi?SID=$SID',
                        }
                    }
                }
            }
        };     
        
        \$('#past_academ_years').datagrid({title:'������ ������� ������. �����'}).datagrid('subgrid', conf);       
       ///////////////////////////////////////////////////////////////////////////
	   
	   
	   //������ ����� ����������� ������ ��� ��������� ����� ����� � ������
       \$('#list_of_pays').datagrid('getPanel').panel('panel').attr('tabindex',0).bind('contextmenu',function(e){
               e.preventDefault();
               \$('#mm_summ').menu('show', {
                   left: e.pageX,
                   top: e.pageY
               });
           });
        ////////////////////////////////////////////
	      

       //////////////////���������� ��������� ��� ����������� �� ���������. �������� ������� ����������� ��������
	   scheduler.clearAll();
	   scheduler.load("get_calendar_events_students.cgi?SID=$SID"+"&num_dog="+row.Num_dogovor,"json");		
	   scheduler.updateView();   
       ///////////////////////////////////////////////////////////////////
		
	   //���������� ���� � ������ ���������� ��� �����
       \$('#panel_comment').panel({
             height:150,
             title:'����������� � ������',
             border: false
       });
        
        
       \$('#comment').textbox({
             multiline:true,
             readonly:true,
             width: 300,
             height:100
       })
       //////////////////////////////////////
	   
	   //��������� � ������� ������ ���������� ���������� ���������
        \$('#visited_events').datagrid({       
        title: '���������� �����������:',
        method:'get',
        showFooter: false,
        scrollbarSize: 0,
        striped: true,
        border: false,
        singleSelect: true,
        url:'get_visited_events.cgi?id_z5='+row.Num_dogovor+'&SID=$SID',
        columns:[[
                 {field:'ID',title:'ID', hidden: true},
                 {field:'NUM_DOG',title:'����� ��������', hidden: true},
                 {field:'KIND_EVENT',title:'KIND_EVENT', hidden: true},
                 {field:'DATE_VISIT',title:'���� ���������', width:100},                 
                 {field:'NAME_EVENT',title:'��� �����������', width:200},
                 {field:'FEEDBACK',title:'�����', width:200}                 
               ]]
        });       
        //////////////////////////////////////////
		
		//��������� � ������� ������ ������������ �����
        \$('#wp').datagrid({       
        title: '������������ ������',
        method:'get',
        scrollbarSize: 0,
        striped: true,
        border: false,
        singleSelect: true,
        url:'get_pays_without_group.cgi?id_zwp='+row.Num_dogovor+'&SID=$SID',
        columns:[[
                 {field:'ID', title:'ID', hidden:true},
                 {field:'PUPILS_NUM_DOGOVOR',title:'PUPILS_NUM_DOGOVOR', hidden:true},                 
                 {field:'OPL_SUMM',title:'���������� �����'},
                 {field:'DATE_OF_PAY',title:'���� ������'},
                 {field:'STATUS',title:'������'},
				 {field:'NOTES',title:'����������'}
               ]]
        });       
        //////////////////////////////////////////
		
	    //������� ���������� ������� � �� �������� ��� �������� ����� ����������, � ����� ���������� ������� � �� ������� ��������������
        \$("#ls").hide();
        \$("#ph").hide();
        \$("#ls_past").hide();
        \$("#ph_past").hide();
       	   
                                }
                        });
                });
       </script>
	   
	   <script> //��������� ����������� ��� ������ ������
       \$(function(){
       \$('#list_of_pays').datagrid({
        onSelect:function(index){
       	                           var row_comment = \$('#list_of_pays').datagrid('getSelected');       	                          
       	                           //////////////////////////////////////////////////////////////////////////
       	                           var ss_cooment = [];
                                   ss_cooment.push(row_comment.ID);
                                   \$.ajax({            
                                    type: 'GET',
                                    traditional: true,
                                    url: 'get_pay_comment.cgi?SID=$SID',
                                    data: {'data':ss_cooment},            
                                    success: function(res) {
                                                               \$('#comment').textbox('setText', res.result); 
                                                           },
                                    error: function() {
                                                         \$('#comment').textbox('clear');                                                                                                             
                                                      }
         
         
                                    });       
                                    ///////////////////////////////////////////////////////////////////////////
       	
       	
       	                        }
                        });
        });
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

       <script>//������� ��������� ������ ���������� �������� �� ������������ ������
       \$(function(){
	   
       \$('#dg').datagrid({
	    rowStyler: function(index,row){
		if (row.MARK_FROM_ZAYAV==1){
			return 'background-color:#6293BB;color:#fff;'; // return inline style
			// the function can return predefined css class and inline style
			// return {class:'r1', style:{'color:#fff'}};	
		}
	    }
        });
		
		\$('#TYPE_GROUP').combogrid({
	    rowStyler: function(index,row){
		if (row.SHOW_COLOR==1){
			return 'background-color:#ffd6ae;color:#0a468c;'; // return inline style				
		}
	    }
        });
		
		\$('#dg').datagrid({
	    rowStyler: function(index,row){
		if (row.IS_MOVED==1){
			                   return 'background-color:#eff11d;color:000000;'; 
			                }
	                    }
        });  
		
        });
        </script>

        <script type="text/javascript">
        var url;
        function newUser(){
            \$('#dlg_student').dialog('open').dialog('center').dialog('setTitle','����� �������');
                        \$('#PASSP').show();
	     \$('#NUM_PASSP').show();
	     \$('#KEM_VIDAN').show();
	     \$('#KOGDA_VIDAN').show();		
            \$('#fm_student').form('clear');
            url = 'insert_student.cgi?SID=$SID';
            \$('#dt_fil').datebox('setValue', Date());
        }
        function editUser(){
            var row = \$('#dg').datagrid('getSelected');
            if (row){
            \$('#dlg_student').dialog('open').dialog('center').dialog('setTitle','�������������� ��������');
            \$('#fm_student').form('load',row);               
            url = 'edit_student.cgi?id_x='+row.Num_dogovor+'&SID=$SID';                                          

             if ((\$('#FIO_PARENT').val().length)>1)
            {
                \$('#PASSP').hide();
		\$('#NUM_PASSP').hide();
		\$('#KEM_VIDAN').hide();
		\$('#KOGDA_VIDAN').hide();		
                \$('#var1').show();
            }
            else
            {
                \$('#PASSP').show();
		\$('#NUM_PASSP').show();
		\$('#KEM_VIDAN').show();
		\$('#KOGDA_VIDAN').show();		
                \$('#var1').hide();
            }

            }
        }
        
        function saveUser() {
        var msg   = \$('#fm_student').serialize();
        \$.ajax({
          type: 'GET',
          url: url,
          data: msg,
          success: function(res) {\$.messager.alert('����������',res.result,'info'); if (res.result=="������� �������� �������!") { \$('#var1').hide(); \$('#fm_student').form('clear'); \$('#dlg_student').dialog('close'); \$('#dg').datagrid('reload');} if (res.result=="������� �������������� �������!") {\$('#var1').hide(); \$('#fm_student').form('clear'); \$('#dlg_student').dialog('close'); \$('#dg').datagrid('reload');}  },
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
		
                                      scheduler.templates.event_bar_date = function(start,end,ev){
                                      return "� <b>"+scheduler.templates.event_date(start)+" - "+scheduler.templates.event_date(end)+"</b> ";
                                      };
        	
		
	}
        </script>

        <script> 
        \$(function(){
         ///////////////�������� �������� ��������.   
        \$('#dt_born').datebox({
	onSelect: function(date){
	        var dt_cur = new Date(); // ����������� ���������� ������� ����
                var res=dt_cur.getFullYear()-date.getFullYear();
		if (res<18)
		{
		    \$.messager.alert('����������','������� ����� 18 ���, ���������� ������ ������ ��������!','info');
                                          \$('#PASSP').hide();
		    \$('#NUM_PASSP').hide();
		    \$('#KEM_VIDAN').hide();
		    \$('#KOGDA_VIDAN').hide();
		    \$('#var1').show();
		}
                                     else
		{
 		    \$('#var1').hide();
                                          \$('#PASSP').show();
		    \$('#NUM_PASSP').show();
		    \$('#KEM_VIDAN').show();
		    \$('#KOGDA_VIDAN').show();	
		}		
			}
        });
        ////////////////////////////////////////////
        
        /////////////////������� ����� ���� � ��������� ��� �������� ���� ���������� �������
        \$('#dlg_student').dialog({
	onClose: function(){
	       \$('#var1').hide();
		           }
        });        
        ////////////////////////////////////////////
                
        });
        </script>
   
       <script>
        var ur;
        function open_window_tie_doc(){
        var row_stud = \$('#dg').datagrid('getSelected');        
            if (row_stud){
            \$('#dlg_tie_doc_2_student').window('open').dialog('center').dialog('setTitle','�������� ��������� � ��������');
            \$('#num_dog_stud').val(row_stud.Num_dogovor);
            ur = 'tie_docum_2_student.cgi?SID=$SID';
            \$('#PRICE_COURSE').numberbox('setValue', '0.00');
            }
        }        
        
        function tie_doc(){
        var msg   = \$('#fm_tie').serialize();
        \$.ajax({
          type: 'GET',
          url: ur,
          data: msg,
          success: function(res) {\$.messager.alert('����������',res.result,'info'); if (res.result=="�������� �������� �������!") {\$('#fm_tie').form('clear'); \$('#dlg_tie_doc_2_student').dialog('close'); \$('#list_of_docum').datagrid('reload');}}, 
          error: function() {alert("did not work");}        
        });
            
        }
        </script>
        
        <script> 
        \$(function(){
        \$('#TYPE_DOC').combobox({
	onSelect: function(rr){
	    var type_id=\$(this).combobox('getValue');
	    \$('#TEXT_DOCUM').combobox({url: 'get_templates.cgi?SID=$SID&id_tmpl='+type_id, method: 'get'});
                              }
                            })
                        })
        </script>
        
          <script> 
        \$(function(){
        \$('#TYPE_GROUP').combogrid({
         panelWidth:700,
		 panelHeight:400,
         idField:'id',
         textField:'text',
		 method: 'get',
         url:'get_groups_list.cgi?SID=$SID',
         columns:[[
        {field:'id',title:'ID',width:60, hidden:true},
        {field:'text',title:'��� ������',width:150},
        {field:'PRICE',title:'����',width:80},        
        {field:'TYPE_OPL',title:'��� ������',width:90},
        {field:'DURATION',title:'������������',width:200},
		{field:'DIRECTION_STUDY',title:'����������� ��������',width:200}
         ]]
                           });

            
            })
        </script>
        
        <script>
        \$(function(){            
        //����������� ���������� ckeditor ������ TEXAREA
        \$('#TEXT_OF_DOCUMENT').ckeditor({uiColor:'#FDE0B0', fullPage:true, height:'500'});  
            
        //��������� ���� ��������� ������������ ���������
        \$('#list_of_docum').datagrid({
	onDblClickRow: function(index){
		var row = \$('#list_of_docum').datagrid('getSelected');
	        \$('#tied_doc').window('open');
	        \$('#TEXT_OF_DOCUMENT').val(row.TEXT_DOCUM);
        }
        
        });   
        });
        </script>

        <script> //������� �������� ���������
        function del_Docum_stud(){
            var row = \$('#list_of_docum').datagrid('getSelected');
            if (row){
                \$.messager.confirm('��������','�� �������, ��� ���������� ������� ��������� �������� � ��������?',function(r){
                    if (r){
                            \$.ajax({            
                            type: 'GET',
                            traditional: true,
                            url: 'del_doc_stud.cgi?SID=$SID',
                            data: {'id_doc':row.ID},            
                            success: function(res) {\$.messager.alert('����������',res.result,'info'); if (res.result=="�������� ������ �������!") {\$('#list_of_docum').datagrid('reload');}},
                            error: function() {alert("did not work");}
                            });                       
                  
                          }
                });
            }
        }  
        </script>
       
       <script>//������� ��������� ������ 
       \$(function(){
               
        \$('#list_of_groups').datagrid({
	rowStyler: function(index,row){
			return 'background-color:#e5f1ff;'; // return inline style
			          }
        });
        
        });
        </script>

       <script> //������� �������� �������
       function delete_row_pay(){
            var row = \$('#list_of_pays').datagrid('getSelected');
            if (row){
                      \$.messager.confirm('��������','�� �������, ��� ���������� ������� ��������� ������?',function(r){
                        if (r){
                            \$.ajax({            
                            type: 'GET',
                            traditional: true,
                            url: 'del_period_of_pay.cgi?SID=$SID',
                            data: {'id_pay':row.ID, 'per_pay':row.PERIOD},            
                            success: function(res) {\$.messager.alert('����������',res.result,'info'); if (res.result=="������ ������ �������!") {\$('#list_of_pays').datagrid('reload');}},
                            error: function() {alert("did not work");}
                            });                       
                  
                          }
                      });
					  
                    };
        }          
        </script>
		
		<script>
        function open_window_add_stud_2_group(){
        var row_stud = \$('#dg').datagrid('getSelected');        
            if (row_stud){
            \$('#dlg_add_student_2_group').window('open').dialog('center').dialog('setTitle','�������� �������� � ������');
            \$('#dg_add_student_2_group').datagrid({url: 'get_groups_4_add_2_student.cgi?SID=$SID&br='+row_stud.BRANCH});
            }
        }
        </script>
        
		<script>
        function add_stud_2_group(){
        var row_stud = \$('#dg').datagrid('getSelected');        
            if (row_stud){            
            var ss = [];
            var row_gr = \$('#dg_add_student_2_group').datagrid('getSelected');
            ss.push(row_stud.Num_dogovor);
            ss.push(row_gr.ID);
                      
            \$.ajax({            
            type: 'GET',
            traditional: true,
            url: 'add_student_2_group.cgi?SID=$SID',
            data: {'dat':ss},            
            success: function(res) {\$.messager.alert('����������',res.result,'info'); if (res.result=="������� �������� ������!") {\$('#dlg_add_student_2_group').dialog('close'); \$('#list_of_groups').datagrid('reload');}},
            error: function() {alert("did not work");}
            });            
                         }
        }
        </script>
		
		<script>
        var urr;
        function open_window_add_pay(){
        var r_stud = \$('#dg').datagrid('getSelected');        
            if (r_stud){
            \$('#dlg_add_pay_2_student').window('open').dialog('center').dialog('setTitle','���������� �������');
            \$('#num_dg_stud').val(r_stud.Num_dogovor);
            urr = 'add_pay_of_student.cgi?SID=$SID';
            \$('#SUM_PAY').numberbox('setValue', '0.00');
			\$('#KIND_OPL').combobox('setValue', '');
            \$('#DATE_PAY').datebox('clear');
            }
        }        
        
        function add_pay(){
        var msg   = \$('#fm_pay').serialize();
        \$.ajax({
          type: 'GET',
          url: urr,
          data: msg,
          success: function(res) {\$.messager.alert('����������',res.result,'info'); if (res.result=="������ ������� �������!") {\$('#fm_pay').form('clear'); \$('#dlg_add_pay_2_student').dialog('close'); \$('#list_of_pays').datagrid('reload');}}, 
          error: function() {alert("did not work");}        
        });
            
        }
        </script>
		
		<script>//��������� �������
        function doFilter(){      
                   
        //��������, ������ ���� �� ���� �������� ����������
        if((!\$("#SEX_STUD").prop("checked")) && (!\$("#SRC_ABOUT_US").prop("checked")) && (!\$("#BR").prop("checked")) && (!\$("#erase_filter").prop("checked")))
        {
	    \$.messager.alert('��������','�� ������ �������� ����������!','warning');
	    return;
        } 
         
        //������ �� ������������ ������� ����� � �������� ��� �������� ��� � ������ � ����������
        var ss=[];            //����� ������ �������� ����� � �������� ��� ����������
        var lb_fl=[];         //����� ������ ����� checkbox-�� ��� ������ �������������� ������ � ���, ����� ������� ��������
        
        \$('#fm_filter input:checkbox:checked').each(function(){            
                        
            ///////�������� �������� � ������, ���� �������� ���� "����� �������"
            if(\$("#erase_filter").prop("checked"))
            {       
                \$('#dg').datagrid('load',{ erase_filter: 'erase_filter' });         
                \$('#lb').text('');
                 return;
            }
            ///////////////////////////////////////
            
            ss.push(\$(this).val()); //��������� � ������ �������� ���� �� �������� ����� �����������
            ss.push(\$('.'+\$(this).attr('id')).combobox('getValue')); //��������� � ������ �������� �� combobox, ������� �������� � checkbox ID �� �������� ������
            lb_fl.push(\$(this)[0].nextSibling.nodeValue.slice(0,-1)); //�������� � ������ ����� checkbox-�� � �������� � ������� slice(0,-1) ��������� ������� ":"
        });         
        
                
        if (ss.length>0)
        {
            ///////////��������� �������� � �������, �� ���������� ����� ��� ����������
            for(var i=0; i<=ss.length; i++) 
            {
                 if (ss[i]=='')
                 {
                      \$.messager.alert('��������','������� �������, �� �� ��� ��������, ��������������� ����� �������, �������!','warning');
                      return;
                      break;
                 }
            }
            /////////////////////
            
          //���� ��� � �������, �� �������� ������ � ������, �������������� ��������������� ��� � ������
          \$('#dg').datagrid('load',{ data_filter: ss.join(',') });
          \$('#lb').text('���������� ������ ��: '+lb_fl);           
        }
    }
        </script>
        
        <script>
        \$(function(){
         \$("#erase_filter").change(function() {
           if(this.checked)
           {
             \$("#SEX_STUD").prop('checked', false);
             \$("#SRC_ABOUT_US").prop('checked', false);
             \$("#BR").prop('checked', false);
           }
                                            }); 
                                            
          \$("#SEX_STUD, #SRC_ABOUT_US, #BR").change(function() {
           if(this.checked)
           {
             \$("#erase_filter").prop('checked', false);             
           }
                                            }); 
         });
        </script>
		
		<script> //����������� ������ �� ������� Enter
        \$(document).ready(function(){
	    var t = \$('#fio');
		var n = \$('#n_dogovor');
		var t_p = \$('#fio_parent');
		
		/////////////////////////
	    t.textbox('textbox').bind('keydown', function(e){
	    if (e.keyCode == 13) 
	    { 
	       doSearch();
	    }
	    });	
		
		/////////////////////////
	    n.numberbox('textbox').bind('keydown', function(e){
	    if (e.keyCode == 13) 
	    { 
	      doSearch();
	    }
	    });
		
		////////////
	    t_p.textbox('textbox').bind('keydown', function(e){
	    if (e.keyCode == 13) 
	    { 
	      doSearch();
	    }
	    });
        })
        </script>
		
		<script>
        function open_window_change_summ(){
        var row = \$('#dg').datagrid('getSelected');
        if (row){                             
            var row_pay = \$('#list_of_pays').datagrid('getSelected');
            if (row_pay){             
                       \$('#dlg_summ').dialog('open').dialog('center').dialog('setTitle','��������� �����');
                       \$('#id_pay').val(row_pay.ID);
                       \$('#num_dogovor_stud').val(row.Num_dogovor);                       
                      }
            
                }
        }
        </script>
        
        <script>
        function set_new_summ() {
        var msg   = \$('#fm_summ').serialize();
        \$.ajax({
          type: 'GET',
          url: 'change_sum_4_opl.cgi?SID=$SID',
          data: msg,
          success: function(res) { \$.messager.alert('����������',res.result,'info'); if (res.result=="����� �������� �������!") {\$('#fm_summ').form('clear'); \$('#dlg_summ').dialog('close'); \$('#list_of_pays').datagrid('reload');}},          error: function() {alert("did not work");}
         });        
        }
        </script>
		
		<script>
       \$(function(){
            \$('#list_of_groups').datagrid({
                view: detailview,
                detailFormatter:function(index,row){
                    return '<div style="padding:2px"><table class="ddv"></table></div>';
                },
                onExpandRow: function(index,row){
				    var row_stud = \$('#dg').datagrid('getSelected');
                    var ddv = \$(this).datagrid('getRowDetail',index).find('table.ddv');
                    ddv.datagrid({
                        //url:'get_detail_groups.cgi?SID=$SID&id_str='+row.GROUP_ID,
						url:'get_detail_groups.cgi?SID=$SID&id_str='+row_stud.Num_dogovor,
                        method: 'get',
                        fitColumns:true,
                        singleSelect:true,
                        rownumbers:true,
                        loadMsg:'',
                        height:'60px',
                        columns:[[
                            {field:'START_DATE',title:'���� ������',width:80},
                            {field:'END_DATE',title:'���� ���������',width:80},
                            {field:'COURSE_PRICE',title:'��������� �����',width:80},
                            {field:'BEGIN_STUDY',title:'������ ��������',width:90}                            
                        ]],
                        onResize:function(){
                            \$('#list_of_groups').datagrid('fixDetailRowHeight',index);
                        },
                        onLoadSuccess:function(){
                            setTimeout(function(){
                                \$('#list_of_groups').datagrid('fixDetailRowHeight',index);
                            },0);
                        }
                    });
                    \$('#list_of_groups').datagrid('fixDetailRowHeight',index);
                }
            });
        });
        </script>
		
		<script>
        function open_window_move_stud(){
        var row_stud = \$('#dg').datagrid('getSelected');        
            if (row_stud){
                
                 /////�������� ������������ ������ �������� ��� �������� ����
                 var dat = [];
                 dat.push(row_stud.Num_dogovor);
                 \$.ajax({            
                 type: 'GET',
                 traditional: true,
                 url: 'get_group_name_4_move_stud.cgi?SID=$SID',
                 data: {'data':dat},            
                 success: function(res) {
                                          \$('#current_group').text(res.result);
                                        },
                 error: function() {
                                       \$('#current_group').text('');
                                   }         
                });       
                ///////////////////////////////////////////////////////////////////////////
                
               \$('#dlg_move_student').window('open').dialog('center').dialog('setTitle','����������� ��������� ����� ��������');
               \$('#dg_move_student').datagrid({url: 'get_groups_4_move_students.cgi?SID=$SID&br='+row_stud.BRANCH+'&nm_dog='+row_stud.Num_dogovor});               
            }
        }
        </script>
        
        <script>
        function move_stud_2_group(){
        \$.messager.confirm('��������','�� �������, ��� ���������� ����������� �������� � ��������� ������?',function(r){
        if (r){
                var row_stud = \$('#dg').datagrid('getSelected');        
                if (row_stud){                      
                var row_gr = \$('#dg_move_student').datagrid('getSelected');
                if (row_gr){
                var ss = [];
                ss.push(row_stud.Num_dogovor);
                ss.push(row_gr.ID);
                   
                \$.ajax({            
                type: 'GET',
                traditional: true,
                url: 'move_students_between_groups.cgi?SID=$SID',
                data: {'dat':ss},
                success: function(res) {\$.messager.alert('����������',res.result,'info'); if (res.result=="����������� ��������� ������!") {\$('#dlg_move_student').dialog('close'); \$('#list_of_groups').datagrid('reload');}},
                error: function() {alert("did not work");}
                });            
                         
                          } else { \$.messager.alert('��������','�� ������� ������!','warning'); }
                         
                         }
            }
          });
        }
        </script>
		
		//����������� ����������� ������
       <script>
       \$(function(){
           \$('#dg').datagrid('getPanel').panel('panel').attr('tabindex',0).bind('contextmenu',function(e){
               e.preventDefault();
               \$('#mm').menu('show', {
                   left: e.pageX,
                   top: e.pageY
               });
           });
       });
       </script>
       /////////////////////////////////
       
       <script> //������� ����������� �������� � �����
       function move_student(){
            var row = \$('#dg').datagrid('getSelected');
            if (row){
                \$.messager.confirm('��������','�� �������, ��� ���������� ����������� �������� � �����?',function(r){
                    if (r){
                             \$.ajax({            
                             type: 'GET',
                             traditional: true,
                             url: 'move_student_2_archive.cgi?SID=$SID',
                             data: {'id_x1':row.Num_dogovor},
                             success: function(res) {\$.messager.alert('����������',res.result,'info'); if (res.result=="������� ��������� � ����� ������!") {\$('#dg').datagrid('reload');}},
                             error: function() {alert("did not work");}
                             });
                     
                          }   
                });
            }
        }  
        </script>
		
		
	   <script> 
       function find_stud(){ 
       	 var myId1 = $num_dog;
       	 var p_size=\$('#dg').datagrid('options').pageSize;
       	 
       	 \$.ajax({            
            type: 'GET',
            traditional: true,
            url: 'get_page_student.cgi?SID=$SID',
            data: {'n_d':myId1, 'page_size':p_size},            
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
	   
	   <script> 
       \$(function(){
        //���������� ���� TextBox ������� KeyUp ��� ������ �� ����
        \$('#fio').textbox({
	                      inputEvents:\$.extend({},\$.fn.textbox.defaults.inputEvents,{
		              keyup:function(e){
			                          doSearch();
		                               }
	                      })
                           })
        
        
        //���������� ���� NumberBox ������� KeyUp ��� ������ �� ����
        \$('#n_dogovor').textbox({
	                      inputEvents:\$.extend({},\$.fn.numberbox.defaults.inputEvents,{
		              keyup:function(e){
			                          doSearch();
		                               }
	                      })
                           })
						   
		 
		 \$('#fio_parent').textbox({
	                      inputEvents:\$.extend({},\$.fn.textbox.defaults.inputEvents,{
		              keyup:function(e){
			                          doSearch();
		                               }
	                      })
                           })
        
        
        })
        </script>
		
		<script>
        function open_window_add_period_pay(){
        var row = \$('#dg').datagrid('getSelected');
        \$('#SUMM_PAY').numberbox('clear');
        if (row){                             
                   \$('#dlg_add_period_pay').dialog('open').dialog('center').dialog('setTitle','���������� �������');
                   \$('#num_dogovor_student').val(row.Num_dogovor);  
                }
        }
        </script>
        
        <script>
        function add_period_pay() {
        var msg   = \$('#fm_add_period_pay').serialize();
        \$.ajax({
          type: 'GET',
          url: 'add_period_of_pay.cgi?SID=$SID',
          data: msg,
          success: function(res) { \$.messager.alert('����������',res.result,'info'); if (res.result=="������ �������� �������!") {\$('#fm_add_period_pay').form('clear'); \$('#dlg_add_period_pay').dialog('close'); \$('#list_of_pays').datagrid('reload');}},          error: function() {alert("did not work");}
         });        
        }
        </script>
		
		<script>
        function show_orders(){
        var row_st = \$('#dg').datagrid('getSelected');        
            if (row_st){
            \$('#dlg_student_orders').window('open').dialog('center').dialog('setTitle','������ ��������');
            \$('#dg_student_orders').datagrid({url: 'get_student_orders.cgi?SID=$SID&n_dog='+row_st.Num_dogovor});
            }
        }
        </script>
		
		<script>
        \$(function(){
        \$('#list_of_groups').datagrid({
         onDblClickRow:function(index, row){
                                             window.location.href = "sekretariat_groups.cgi?SID=$SID&name_gr="+row.GROUP_ID;        
                                           }
                           
                        });
                });
        </script>
		
		<script>
        function show_orders_past_academ(){
        var row_st1 = \$('#past_academ_years').datagrid('getSelected');        
            if (row_st1){
            \$('#dlg_student_orders_past_academ').window('open').dialog('center').dialog('setTitle','������ ��������');
            \$('#dg_student_orders_past_academ').datagrid({url: 'get_student_orders_past_academ.cgi?SID=$SID&n_dog='+row_st1.PUPILS_NUM_DOGOVOR+'&uuid='+row_st1.UUID});
            }
        }
        </script>
		
		<script>
        \$(function(){
        \$('#dg_student_orders_past_academ').datagrid({   
         method:'get',
         fitColumns: true,
         singleSelect:true,     
         columns:[[
                    {field:'NUM_ORDER',title:'� ������',width:40},
                    {field:'OSNOVANIE',title:'���������',width:150},
                    {field:'SUMM_OPL',title:'���������� �����',width:50},
                    {field:'STATUS',title:'��� �������',width:50},
                    {field:'DATE_PAY',title:'���� �������',width:50},
                    {field:'USER_CREATED_ORDER',title:'����� ��������',width:100}
                 ]]
            });
        });
        </script>
		
		<script>
        var url;
        function newEvent(){
            var row = \$('#dg').datagrid('getSelected');                        
            \$('#KIND_EVENT').combobox('clear');
            \$('#FEEDBACK').textbox('clear');
            \$('#DATE_VISIT').datebox('clear');
            if (row){ 
                      \$('#dlg_visited_event').dialog('open').dialog('center').dialog('setTitle','���������� �����������');
                      \$('#DATE_VISIT').datebox('setValue', Date());
                      \$('#number_dog_st').val(row.Num_dogovor);  
                      url = 'add_event_4_student.cgi?SID=$SID';                      
                    }
        }                
        
        function editEvent(){
            var row = \$('#visited_events').datagrid('getSelected');
            if (row){
	              \$('#dlg_visited_event').dialog('open').dialog('center').dialog('setTitle','�������������� �����������');
                      \$('#DATE_VISIT').datebox('setValue', row.DATE_VISIT);
                      \$('#KIND_EVENT').combobox('setValue', row.KIND_EVENT); 
                      \$('#FEEDBACK').textbox('setValue', row.FEEDBACK);              
                      url = 'edit_event_4_student.cgi?id_event='+row.ID+'&SID=$SID';
                    }
        }
        
        function saveEvent() {            
        var msg   = \$('#fm_visited_event').serialize();
        \$.ajax({
          type: 'GET',
          url: url,
          data: {'date_visit':\$('#DATE_VISIT').datebox('getValue'), 'kind_event':\$('#KIND_EVENT').combobox('getValue'), 'feedback':\$('#FEEDBACK').textbox('getValue'), 'number_dog_st': \$('#number_dog_st').val() },          
          success: function(res) {\$.messager.alert('����������',res.result,'info'); if (res.result=="����������� ��������� �������!") {\$('#fm_visited_event').form('clear'); \$('#dlg_visited_event').dialog('close'); \$('#visited_events').datagrid('reload');} if (res.result=="����������� ��������������� �������!") { \$('#fm_visited_event').form('clear'); \$('#dlg_visited_event').dialog('close'); \$('#visited_events').datagrid('reload');} }, 
          error: function() {alert("did not work");}        
        });
        
           
       }                
       </script>
       
       <script> //������� �������� �����������
       function deleteEvent(){
            var row = \$('#visited_events').datagrid('getSelected');
            if (row){                                            
                       \$.messager.confirm('��������','�� �������, ��� ���������� ������� �����������?',function(r){
                        if (r){
                            \$.ajax({            
                            type: 'GET',
                            traditional: true,
                            url: 'del_visited_events.cgi?SID=$SID',
                            data: {'id_visited_event':row.ID},            
                            success: function(res) {\$.messager.alert('����������',res.result,'info'); if (res.result=="����������� ������� �������!") {\$('#visited_events').datagrid('reload');}},
                            error: function() {alert("did not work");}
                            });                       
                  
                          }
                      });
                      
                    };
        }          
        </script>
		
		<script> //������� ����������� �������� ������� �� ������ �������������.
        \$(function(){
	    function setClick(target){
		var clickHandler = function(e){
			var opts = \$(this).linkbutton('options');
			if (!opts.disabled){
				if (opts.toggle){
					if (opts.selected){
						\$(this).linkbutton('unselect');
					} else {
						\$(this).linkbutton('select');
					}
				}
				opts.onClick.call(this);

				\$(target).unbind('click.linkbutton');
				\$(target).linkbutton('disable');
				\$(target).removeClass('l-btn-disabled l-btn-plain-disabled');
				setTimeout(function(){
					\$(target).linkbutton('enable');
					\$(target).unbind('click.linkbutton').bind('click.linkbutton', clickHandler);
				}, 1000);
			}
		};
		\$(target).unbind('click.linkbutton').bind('click.linkbutton', clickHandler);
	    }
	    \$.extend(\$.fn.linkbutton.methods, {
		 singleClick: function(jq){
			return jq.each(function(){
				setClick(this);
			});
		}
	    })
        });
        
        \$(function(){
	      \$('#but_pay').linkbutton('singleClick');
		  \$('#but_pay_without_gr').linkbutton('singleClick');
        });
        </script>
		
		<script>
        function open_window_add_pay_without_gr(){
        var rec_stud = \$('#dg').datagrid('getSelected');        
            if (rec_stud){
            \$('#dlg_add_pay_2_student_without_group').window('open').dialog('center').dialog('setTitle','���������� �������');
            \$('#num_dg_stud_without_gr').val(rec_stud.Num_dogovor);            
            \$('#SUM_PAY_WITHOUT_GR').numberbox('setValue', '0.00');
            \$('#KIND_OPL_WITHOUT_GR').combobox('setValue', '');
            \$('#DATE_PAY_WITHOUT_GR').datebox('clear');
            \$('#OSNOVANIE_OPL').textbox('clear');
            \$('#NOTES_PAY_WITHOUT_GR').textbox('clear');
            }
        }        
        
        
        function add_pay_without_gr(){
        \$.ajax({
          type: 'GET',
          url: 'add_pay_stud_without_gr.cgi?SID=$SID',
          data: {'num_dg_stud_without_gr':\$('#num_dg_stud_without_gr').val(), 'SUM_PAY_WITHOUT_GR':\$('#SUM_PAY_WITHOUT_GR').numberbox('getValue'), 'NOTES_PAY_WITHOUT_GR':\$('#NOTES_PAY_WITHOUT_GR').textbox('getValue'), 'DATE_PAY_WITHOUT_GR': \$('#DATE_PAY_WITHOUT_GR').datebox('getValue'), 'KIND_OPL_WITHOUT_GR':\$('#KIND_OPL_WITHOUT_GR').combobox('getValue'), 'OSNOVANIE_OPL':\$('#OSNOVANIE_OPL').textbox('getValue')},
          success: function(res) {\$.messager.alert('����������',res.result,'info'); if (res.result=="������ ������� �������!") {\$('#fm_pay_without_gr').form('clear'); \$('#dlg_add_pay_2_student_without_group').dialog('close'); \$('#wp').datagrid('reload');}}, 
          error: function() {alert("did not work");}        
        });
        }
        </script>
		
		<script> //������� ����� � �������� ������ �����
        function move_pays_wg_into_main_pays(){
            var row = \$('#dg').datagrid('getSelected');
            if (row){
                \$.messager.confirm('��������','�� �������, ��� ���������� ��������� ������ � �������� ������ �����?',function(r){
                    if (r){                            
                            \$.ajax({            
                            type: 'GET',
                            traditional: true,
                            url: 'move_pays_into_main.cgi?SID=$SID',
                            data: {'num_dg':row.Num_dogovor},            
                            success: function(res) {\$.messager.alert('����������',res.result,'info'); if (res.result=="������ ���������� �������!") {\$('#wp').datagrid('reload');}},
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
        function show_feedback(){
             var row_num_dog = \$('#dg').datagrid('getSelected');
             var row_id = \$('#home_work').datagrid('getSelected');        
             if (row_id){                
             \$('#window_student_feedback').window('open').dialog('center').dialog('setTitle','����� ��������');
             \$('#dg_student_feedback').datagrid({url: 'get_student_feedback.cgi?SID=$SID&id_lesson='+row_id.ID+'&nm_dogovor='+row_num_dog.Num_dogovor});               }
             else
             {
             \$.messager.alert('��������','���������� ������� ��������� ����!','warning');    
             }        
        }
        </script>
        
        <script>
        \$(function(){
        \$('#dg_student_feedback').datagrid({   
        method:'get',
        fitColumns: true,
        singleSelect:true,     
        columns:[[
                   {field:'ID',title:'ID',hidden:true},
                   {field:'TEXT_FEEDBACK',title:'�����',width:150},
                   {field:'DATETIME_CREATE',title:'���� ������',width:150}                    
                ]]
           });
        });
        </script>
		
		<script> //��������� � ������� ������ ��������� ��������� � ��������� �������
        function open_visits(){ 
        \$("#ls").show();
        \$("#ph").show();  		
        var r_num_dg = \$('#dg').datagrid('getSelected');
        \$('#list_of_students_visits').datagrid({
        title: '������ ��������� � �� ���������',
        method:'get',                                
        showHeader: true,       
        scrollbarSize: 0,
        striped: true,
        border: false,       
        singleSelect: true,
        url:'get_visits_stud.cgi?id_vis='+r_num_dg.Num_dogovor+'&SID=$SID',
        columns:[[
                  {field:'ID',title:'ID', hidden:true},
                  {field:'PERIOD',title:'<b>������</b>'},                                                                                          
                  {field:'DAY1',title:'<b>1</b>', styler:cellStyler},
                  {field:'DAY2',title:'<b>2</b>', styler:cellStyler},
                  {field:'DAY3',title:'<b>3</b>', styler:cellStyler},
                  {field:'DAY4',title:'<b>4</b>', styler:cellStyler},
                  {field:'DAY5',title:'<b>5</b>', styler:cellStyler},
                  {field:'DAY6',title:'<b>6</b>', styler:cellStyler},
                  {field:'DAY7',title:'<b>7</b>', styler:cellStyler},
                  {field:'DAY8',title:'<b>8</b>', styler:cellStyler},
                  {field:'DAY9',title:'<b>9</b>', styler:cellStyler},
                  {field:'DAY10',title:'<b>10</b>', styler:cellStyler},
                  {field:'DAY11',title:'<b>11</b>', styler:cellStyler},
                  {field:'DAY12',title:'<b>12</b>', styler:cellStyler},
                  {field:'DAY13',title:'<b>13</b>', styler:cellStyler},
                  {field:'DAY14',title:'<b>14</b>', styler:cellStyler},
                  {field:'DAY15',title:'<b>15</b>', styler:cellStyler},
                  {field:'DAY16',title:'<b>16</b>', styler:cellStyler},
                  {field:'DAY17',title:'<b>17</b>', styler:cellStyler},
                  {field:'DAY18',title:'<b>18</b>', styler:cellStyler},
                  {field:'DAY19',title:'<b>19</b>', styler:cellStyler},
                  {field:'DAY20',title:'<b>20</b>', styler:cellStyler},
                  {field:'DAY21',title:'<b>21</b>', styler:cellStyler},
                  {field:'DAY22',title:'<b>22</b>', styler:cellStyler},
                  {field:'DAY23',title:'<b>23</b>', styler:cellStyler},
                  {field:'DAY24',title:'<b>24</b>', styler:cellStyler},
                  {field:'DAY25',title:'<b>25</b>', styler:cellStyler},
                  {field:'DAY26',title:'<b>26</b>', styler:cellStyler},
                  {field:'DAY27',title:'<b>27</b>', styler:cellStyler},
                  {field:'DAY28',title:'<b>28</b>', styler:cellStyler},
                  {field:'DAY29',title:'<b>29</b>', styler:cellStyler},
                  {field:'DAY30',title:'<b>30</b>', styler:cellStyler},
                  {field:'DAY31',title:'<b>31</b>', styler:cellStyler}                                                           
               ]]
        });       
        //////////////////////////////////////////	 
                                 
                                 
        //��������� � ������� ������ ��������� ��� � ��
        \$('#home_work').datagrid({
        method:'get',  
        title: '��������� ����/�������� �������',                              
        showHeader: true,       
        scrollbarSize: 0,
        striped: true,
        border: false,
        singleSelect: true,
        fitColumns: true,                                 
        url:'get_homework_stud.cgi?id_hw='+r_num_dg.Num_dogovor+'&SID=$SID',
        columns:[[
                  {field:'ID',title:'ID', hidden:true},
                  {field:'DATE_LESSON',title:'<b>���� �������</b>'},
                  {field:'TOPIC',title:'<b>����</b>'},
                  {field:'HOME_WORK',title:'<b>��</b>'}                                                                                      
               ]]
        });       
        ////////////////////////////////////////// 
        }
        </script>      

        <script>
        function show_past_visits(){
             var row_past_visits = \$('#past_academ_years').datagrid('getSelected');
             if (row_past_visits){                
             \$("#ls_past").show();
             \$("#ph_past").show();        
             \$('#past_visits').datagrid({
             title: '������ ���������',
             method:'get',                                
             showHeader: true,       
             scrollbarSize: 0,
             striped: true,
             border: false,       
             singleSelect: true,
             url:'get_past_visits_stud.cgi?uuid_past_vis='+row_past_visits.UUID+'&SID=$SID',
             columns:[[
                       {field:'ID',title:'ID', hidden:true},
                       {field:'PERIOD',title:'<b>������</b>'},                                                                                          
                       {field:'DAY1',title:'<b>1</b>', styler:cellStyler},
                       {field:'DAY2',title:'<b>2</b>', styler:cellStyler},
                       {field:'DAY3',title:'<b>3</b>', styler:cellStyler},
                       {field:'DAY4',title:'<b>4</b>', styler:cellStyler},
                       {field:'DAY5',title:'<b>5</b>', styler:cellStyler},
                       {field:'DAY6',title:'<b>6</b>', styler:cellStyler},
                       {field:'DAY7',title:'<b>7</b>', styler:cellStyler},
                       {field:'DAY8',title:'<b>8</b>', styler:cellStyler},
                       {field:'DAY9',title:'<b>9</b>', styler:cellStyler},
                       {field:'DAY10',title:'<b>10</b>', styler:cellStyler},
                       {field:'DAY11',title:'<b>11</b>', styler:cellStyler},
                       {field:'DAY12',title:'<b>12</b>', styler:cellStyler},
                       {field:'DAY13',title:'<b>13</b>', styler:cellStyler},
                       {field:'DAY14',title:'<b>14</b>', styler:cellStyler},
                       {field:'DAY15',title:'<b>15</b>', styler:cellStyler},
                       {field:'DAY16',title:'<b>16</b>', styler:cellStyler},
                       {field:'DAY17',title:'<b>17</b>', styler:cellStyler},
                       {field:'DAY18',title:'<b>18</b>', styler:cellStyler},
                       {field:'DAY19',title:'<b>19</b>', styler:cellStyler},
                       {field:'DAY20',title:'<b>20</b>', styler:cellStyler},
                       {field:'DAY21',title:'<b>21</b>', styler:cellStyler},
                       {field:'DAY22',title:'<b>22</b>', styler:cellStyler},
                       {field:'DAY23',title:'<b>23</b>', styler:cellStyler},
                       {field:'DAY24',title:'<b>24</b>', styler:cellStyler},
                       {field:'DAY25',title:'<b>25</b>', styler:cellStyler},
                       {field:'DAY26',title:'<b>26</b>', styler:cellStyler},
                       {field:'DAY27',title:'<b>27</b>', styler:cellStyler},
                       {field:'DAY28',title:'<b>28</b>', styler:cellStyler},
                       {field:'DAY29',title:'<b>29</b>', styler:cellStyler},
                       {field:'DAY30',title:'<b>30</b>', styler:cellStyler},
                       {field:'DAY31',title:'<b>31</b>', styler:cellStyler}                                                           
                     ]]
             });       
             //////////////////////////////////////////	 
                                 
                                 
             //��������� � ������� ������ ��������� ��� � �� � ������� ��������
             \$('#past_home_work').datagrid({
             method:'get',  
             title: '��������� ����/�������� �������',                              
             showHeader: true,       
             scrollbarSize: 0,
             striped: true,
             border: false,
             singleSelect: true,
             fitColumns: true,                                 
             url:'get_past_homework_stud.cgi?uuid_past_hw='+row_past_visits.UUID+'&SID=$SID',
             columns:[[
                       {field:'ID',title:'ID', hidden:true},
                       {field:'DATE_LESSON',title:'<b>���� �������</b>'},
                       {field:'TOPIC',title:'<b>����</b>'},
                       {field:'HOME_WORK',title:'<b>��</b>'}                                                                                      
                     ]]
             });       
             ////////////////////////////////////////// 
             }
             else
             {
             \$.messager.alert('��������','���������� ������� ������!','warning');    
             }                  
        }
        </script> 		
		
		<script>
        function show_past_feedback(){
             var row_past_per = \$('#past_academ_years').datagrid('getSelected');
             if (row_past_per){                
             \$('#window_student_past_feedback').window('open').dialog('center').dialog('setTitle','������ ��������');
             \$('#dg_student_past_feedback').datagrid({url: 'get_student_past_feedback.cgi?SID=$SID&uuid_past_feedback='+row_past_per.UUID});               }
             else
             {
             \$.messager.alert('��������','���������� ������� ������!','warning');    
             }        
        }
        </script>     
        
        <script>
        \$(function(){
        \$('#dg_student_past_feedback').datagrid({   
        method:'get',
        fitColumns: true,
        singleSelect:true,     
        columns:[[
                   {field:'ID',title:'ID',hidden:true},
                   {field:'TOPIC',title:'���� �������',width:150},
                   {field:'TEXT_FEEDBACK',title:'�����',width:150}                    
                ]]
           });
        });
        </script> 
		

        </head>
HTML

        if (defined($num_dog))
        {
            print qq(<body class="easyui-layout" onload="init(); setTimeout('find_stud()',1000)">);
        }
        else
        {
            $num_dog = 0;
			print qq(<body class="easyui-layout" onload="init();">);
        }
    
        print <<HTML2;
		<!--������� DIV - ��������� -->
        <div data-options="region:'north',border:false" style="height:100px;background:#f0993c;padding:10px"><h1 class="shd">@name_org</h1>
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
        <div class="easyui-tabs" style="width:100%;height:auto" data-options="narrow:true, fit:true">
         <div title="�����">
         <table id="pg" style="width:100%"></table>
         </div>
         <div title="������">

            <!--������ �������� �������� � ������ -->
            <div style="padding:10px 10px;">
            <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-add'" onclick="open_window_add_stud_2_group()">��������� � ������</a>
			<a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-add'" onclick="open_window_move_stud()">����������� ����� ��������</a>
            </div>
            <!--����� ������ �������� �������� � ������ -->
            
            <!-- ����� ������ ����� � ������� �������� �������-->
            <table id="list_of_groups"></table>
            <!-- ����� ����� ������ ����� � ������� �������� ������� -->

         </div>
         <div title="�������"">

         <!--������ ���������� ������� � ������� � �������� ������� -->
         <div style="padding:10px 10px;">
         <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-add'" onclick="open_window_add_pay()">�������� ������</a>
		 <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-add'" onclick="open_window_add_period_pay()">�������� ������</a>
         <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-remove'" onclick="delete_row_pay()">������� ������</a>
		 <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-list'" onclick="show_orders()">������</a>
         </div>
         <!--����� ������ ���������� ������� � ������� � �������� ������� -->
		 
		 <!--������� �������� ������, ������ ��������� ����� � ������� ���������� �������-->
         <div style="margin-bottom: 10px;">
          <span id="group" style="font-weight: bold; float: left;"></span>
          <div id="p" style="width:auto; height:15px; bold;"></div> 
          </br>
          <span id="paid" style="font-weight: bold;"></span>         
		  </br>          
          <div style="margin-top: 10px;"><span id="debt_4_today" style="font-weight: bold;"></span></div>
         </div>         
         <!--����� ������� �������� ������, ������ ��������� ����� � ������� ���������� �������-->

         <!-- ����� ������ ����� ��������-->
         <table id="list_of_pays"></table>
         <!-- ����� ����� ������ ����� �������� -->
		 
		 <!-- ����� ������������ � �������-->
         <div style="margin-top:10px;">
          <div id="panel_comment">
           <input name="comment" id="comment" style="width:0px;">
          </div>
         </div>
         <!-- ����� ����� ������������ � ������� -->

         </div>
		 
         <div title="��������� � ��">
          
		   <div id="bt" style="margin-left:10px; margin-top:10px; margin-bottom:10px;">           
             <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-list'" onclick="open_visits()">����������</a>           
           </div>           
           <div id="ls" style="margin-left:10px; margin-top:10px;">
             <table id="list_of_students_visits" style="width:100%"></table>
           </div>
           <div id="ph" style="margin-top:20px; margin-left:10px;">
            <table id="home_work" class="easyui-datagrid" style="width:100%" toolbar="#dlg-buttons_feedback"></table>             
           </div>
           <div id="dlg-buttons_feedback">          
            <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="show_feedback()">�������� ������</a>           
           </div>       
          
         </div>
		 
         <div title="���������">

            <!--������ �������� � �������� ��������� -->
            <div style="padding:10px 10px;">
            <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-add'" onclick="open_window_tie_doc()">��������� ��������</a>
            <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-remove'" onclick="del_Docum_stud()">������� ��������</a>
            </div>
            <!--����� ������ �������� � �������� ���������� -->
            
             <!-- ����� ������ ����������� ���������� � �������� -->
            <table id="list_of_docum"></table>
            <!-- ����� ����� ������ ����������� ���������� � �������� -->

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
       
	     <div title="���������� �����������">
         <!--������ ���������� �������������-->
          <div style="padding:10px 10px;">
             <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-add'" onclick="newEvent();">��������</a>
             <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-edit'" onclick="editEvent();">�������������</a>
             <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-remove'" onclick="deleteEvent();">�������</a>
          </div>
          <!--����� ������ ���������� ������������� -->
          <table id="visited_events" style="width:100%"></table>
         </div>
	   
         <div title="������� ��������">
         <table id="hs" style="width:100%"></table>
         </div>
		 <div title="������� ������.����">
		 <!--������ �������� ������� � ������� ������ ��������-->
           <div style="padding:10px 10px;">
             <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-list'" onclick="show_orders_past_academ()">������</a>
			 <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-list'" onclick="show_past_visits()">��������� � ��</a>
           </div>
           <!--����� ������ �������� ������� � ������� ������ ��������-->
		   <table id="past_academ_years" style="width:100%"></table>
		   <div id="ls_past" style="margin-left:10px; margin-top:10px;">           
             <table id="past_visits" style="width:100%"></table>
           </div>
          <div id="ph_past" style="margin-top:20px; margin-left:10px;">
            <table id="past_home_work" class="easyui-datagrid" style="width:100%" toolbar="#dlg-buttons_past_feedback"></table>             
          </div>
		  <div id="dlg-buttons_past_feedback">          
            <a href="#" class="easyui-linkbutton" iconCls="icon-list" plain="true" onclick="show_past_feedback()">�������� ������</a>           
          </div>  
         </div>
		 
		 <div title="������������ ������">
         <!--������ ���������� �������-->
         <div style="padding:10px 10px;">
         <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-add'" onclick="open_window_add_pay_without_gr()">�������� ������</a>
         <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-remove'" onclick="delete_pay_without_group()">������� ������</a>
		 <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-list'" onclick="move_pays_wg_into_main_pays()">��������� ������</a>
         </div>
         <!--����� ������ ���������� �������-->
         
         <table id="wp" style="width:100%"></table>   
                       
         </div>
		 
        </div>
        <!-- ����� ������ TABS -->
        
        </div>
        <!-- ����� ������ DIV ������ ����������� -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->
        
        <!-- ����������� DIV -������� ������� --> 
        <div data-options="region:'center',title:'������� ������� - ��������. ������������: $formLogin'">

        <table id="dg" title="��������" class="easyui-datagrid" style="width:100%;height:95%"
        method="get"
        url="get_students.cgi?SID=$SID"
        toolbar="#tb, #toolbar"
        rownumbers="true" fitColumns="true" singleSelect="true" pagination="true" sortName="Num_dogovor" sortOrder="asc" idField="Num_dogovor" pageSize="50">
        <thead>
        <tr>
            <th field="Num_dogovor" width="15" sortable="true">�������</th>
			<th field="FIO" width="150" sortable="true">���</th>
            <th field="MOBILE_PHONE" width="30">���.���.</th>
            <th field="HOME_PHONE" width="20">���.���.</th>
            <th field="MARK_FROM_ZAYAV" width="2" hidden="true">MARK_FROM_ZAYAV</th>
        </tr>
        </thead>
        </table>
        <div id="toolbar">
        <!-- <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="newUser()">�������� ��������</a> -->
        <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="editUser()">������������� ��������</a>
		<a href="#" class="easyui-linkbutton" iconCls="icon-filter" plain="true" onclick="\$('#dlg_filter').window('open').dialog('center').dialog('setTitle','������')">������</a>
        <span id="lb" style="float:right; color: #F00; font-weight: bold;"></span>
        </div>

        <!-- ������ ������ -->
        <div id="tb" style="padding:3px">
             <span>����� �� ���:</span>
             <input id="fio" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
			 <span>����� �� ��� ��������:</span>
             <input id="fio_parent" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
			 <span>����� �� ��������:</span>
             <input id="n_dogovor" class="easyui-numberbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
             <a href="#" class="easyui-linkbutton" plain="false" onclick="doSearch()" style="border-radius:5px; width:100px;">������</a>
        </div>
        <!-- ����� ������ ������ -->

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

    <!-- ����� ���������� ������ �������� -->    
    <div id="dlg_student" class="easyui-dialog" style="width:515px;height:600px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons_student" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">���������� � ��������</div>
        <form id="fm_student" novalidate>     
         
         <div class="fitem">
                <label><b>������ ������.</b></label>
                </div>
         <div class="fitem">
               <label>��� ��������:</label>
               <input name="FIO" class="easyui-textbox" required missingMessage="������ ���� ���������� ���������">
	        </div>
	 <div class="fitem">
       	        <label>���� ��������:</label>
           	<input id="dt_born" name="DATE_OF_BORN" class="easyui-datebox" data-options="required:true, formatter:myformatter, parser:myparser" missingMessage="������ ���� ���������� ���������">
           	</div>
         <div class="fitem" id="PASSP">
               	<label>����� ��������:</label>
               	<input name="PASSPORT" class="easyui-numberbox">
	        </div>
	 <div class="fitem" id="NUM_PASSP">
               	<label>����� ��������:</label>
               	<input name="PASSPORT_NUM" class="easyui-numberbox">
	        </div>
	 <div class="fitem"  id="KEM_VIDAN">
               	<label>��� �����:</label>
               	<input name="PASSPORT_VIDAN" class="easyui-textbox">
	        </div>
	 <div class="fitem" id="KOGDA_VIDAN">
               	<label>����� �����:</label>
               	<input name="PASSPORT_DATE" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser">
	        </div>
	 <div class="fitem">
               	<label>���:</label>
               	<select name="SEX" class="easyui-combobox" style="width:263px;" data-options="panelHeight:'auto', required:true" missingMessage="������ ���� ���������� ���������">
               	<option>�</option>
                   <option>�</option>
                   </select>
           	 </div>
                   <!-- ���� ����� ���������� � ��������. ����������� ���� ������� ����� 14 ���. -->
                 <div  id="var1" style="display: none;">
                 <div class="fitem">
                <label><b>������ � ��������.</b></label>
                </div>
                <div class="fitem">
               <label>���:</label>
               <input id="FIO_PARENT" name="FIO_PARENT" class="easyui-textbox">
	        </div>
	 <div class="fitem">
               	<label>����� ��������:</label>
               	<input name="SER_PASSPORT_PARENT" class="easyui-numberbox">
	        </div>
	 <div class="fitem">
               	<label>����� ��������:</label>
               	<input name="NUM_PASSPORT_PARENT" class="easyui-numberbox">
	        </div>
	 <div class="fitem">
               	<label>��� �����:</label>
               	<input name="KEM_VIDANO_PASSPORT_PARENT" class="easyui-textbox">
	        </div>
	 <div class="fitem">
               	<label>����� �����:</label>
               	<input name="KOGDA_VIDANO_PASSPORT_PARENT" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser">
	        </div>
                   </div>
         <!-- ����� ���� ����� ���������� � ��������. ����������� ���� ������� ����� 14 ���. -->
         <div class="fitem">
                <label><b>���������� ����������.</b></label>
                </div>
         <div class="fitem">
               	<label>�������� �����:</label>
               	<input name="HOME_ADDRESS" class="easyui-textbox" data-options="required:true" missingMessage="������ ���� ���������� ���������">
	        </div>
	 <div class="fitem">
               	<label>�������� �������:</label>
               	<input name="HOME_PHONE" class="easyui-textbox">
	        </div>
	 <div class="fitem">
               	<label>������� �������:</label>
               	<input name="WORK_PHONE" class="easyui-textbox">
	        </div>
	 <div class="fitem">
               	<label>��������� �������:</label>
               	<input name="MOBILE_PHONE" class="easyui-textbox">
	        </div>
	 <div class="fitem">
               	<label>���. ���. �������:</label>
               	<input name="MOBILE_CHILD" class="easyui-textbox">
	        </div>
	 <div class="fitem">
               	<label>Email:</label>
               	<input name="EMAIL" class="easyui-validatebox textbox" data-options="required:true,validType:'email'">
	        </div>
	 <div class="fitem">
               	<label>����� ������/�����:</label>
               	<input name="PLACE_OF_WORK" class="easyui-textbox">
	        </div>
	 <div class="fitem">
               	<label>���������/���������:</label>
               	<input name="POSITION_FACULT" class="easyui-textbox">
	        </div>
	 <div class="fitem">
                   <label><b>���������� �� ��������.</b></label>
                          </div>
                     <div class="fitem">
               	<label>������:</label>
               	<input name="BRANCH" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_branches.cgi?SID=$SID', method: 'get'" missingMessage="������ ���� ���������� ���������">
                         </div>
	 <div class="fitem">
                  <label><b>���������� �� ����������.</b></label>
                        </div>
	 <div class="fitem">
               	<label>���� ����������:</label>
               	<input id="dt_fil" name="DATE_OF_FILLING" class="easyui-datebox" data-options="required:true, formatter:myformatter, parser:myparser" missingMessage="������ ���� ���������� ���������">
	        </div>
	 <div class="fitem">
                  <label><b>������ � ��� ������.</b></label>
                          </div>
                   <div class="fitem">
               	<label>�������� ����������:</label>
               	<input name="SOURCE_ABOUT_US" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_source_about_us.cgi?SID=$SID', method: 'get'">
           	</div>         
                   <div class="fitem">
                <label><b>�������������.</b></label>
                </div>
                <div class="fitem">
               	<label>����������:</label>
               	<input name="STUDENT_INTERESTS" class="easyui-textbox" data-options="multiline:true" style="height:100px">
	        </div>
	 <div class="fitem">
               	<label>�������� �� ��������� SMS:</label>
               	<input name="AGREMMENT_GET_SMS" class="easyui-switchbutton" value="1" data-options="onText:'��',offText:'���'">
	        </div>
	 <div class="fitem">
               	<label>�������� �� ��������� E-mail:</label>
               	<input name="AGREMMENT_GET_EMAIL" class="easyui-switchbutton" value="1" data-options="onText:'��',offText:'���'">
	        </div>
	 <div class="fitem">
               	<label>�������� �� ������������� �����������:</label>
               	<input name="AGREMMENT_USE_PHOTO" class="easyui-switchbutton" value="1" data-options="onText:'��',offText:'���'">
	        </div>
	 <div class="fitem">
               	<label>�������� �� �������:</label>
               	<input name="BARTER" class="easyui-switchbutton" value="1" data-options="onText:'��',offText:'���'">
	        </div>
	 <div class="fitem">
               	<label>�������������� ��������:</label>
               	<input name="INDIVIDUAL" class="easyui-switchbutton" value="1" data-options="onText:'��',offText:'���'">
	        </div>
        </form>
    </div>
    <div id="dlg-buttons_student">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="saveUser()" style="width:100px">���������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript: \$('#var1').hide(); \$('#dlg_student').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� ���������� ������ �������� -->

    <!-- ����� �������� ��������� � �������� -->    
    <div id="dlg_tie_doc_2_student" class="easyui-dialog" style="width:330px;height:480px;padding:10px 1px;"
            closed="true" modal="true" buttons="#dlg-buttons_tie" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">�������� ���������</div>
        <form id="fm_tie" novalidate>
           <div class="fitem">
               	<label>��� ���������:</label>
               	<input id="TYPE_DOC" name="TYPE_DOC" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_type_docs.cgi?SID=$SID', method: 'get'" missingMessage="������ ���� ���������� ���������">
           	</div>
           <div class="fitem">
               	<label>����:</label>
               	<input id="COURSE" name="COURSE" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'400px', valueField: 'id', textField: 'text', groupField:'group', url: 'get_kind_prog.cgi?SID=$SID', method: 'get'" missingMessage="������ ���� ���������� ���������">
           	</div>
           <div class="fitem">
               	<label>��� ������:</label>
               	<input id="TYPE_GROUP" name="TYPE_GROUP">
           	</div>
           <div class="fitem">
               	<label>���� ����� (&#8381;):</label>
               	<input id="PRICE_COURSE" name="PRICE_COURSE" class="easyui-numberbox" data-options="precision:2">
           	</div>           
           <div class="fitem">
               	<label>���� ��������:</label>
               	<input name="DATE_START_DOGOVOR" class="easyui-datebox" data-options="required:true, formatter:myformatter, parser:myparser" missingMessage="������ ���� ���������� ���������">
	        </div>
	   <div class="fitem">
               	<label>���� ��������� ��������:</label>
               	<input name="DATE_END_DOGOVOR" class="easyui-datebox" data-options="required:true, formatter:myformatter, parser:myparser" missingMessage="������ ���� ���������� ���������">
	        </div>
           <div class="fitem">
               	<label>������:</label>
               	<input id="TEXT_DOCUM" name="TEXT_DOCUM" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text'" missingMessage="������ ���� ���������� ���������">
           	</div>
            
            <input name="num_dog_stud" type="hidden" id="num_dog_stud" value="" />
               
        </form>
    </div>
    <div id="dlg-buttons_tie">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="tie_doc()" style="width:100px">���������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_tie_doc_2_student').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� �������� ��������� � �������� -->
    
    <!-- ���� ����������� ������������ ��������� -->
    <div id="tied_doc" class="easyui-window" title="���������� ���������" style="width:100%;height:100%;"
        data-options="iconCls:'icon-print',modal:true,closed:true">
        <textarea name="TEXT_OF_DOCUMENT" id="TEXT_OF_DOCUMENT"></textarea>               
    </div>
    <!-- ����� ���� ����������� ������������ ��������� -->
	
	<!-- ����� �������� �������� � ������ -->    
    <div id="dlg_add_student_2_group" class="easyui-dialog" style="width:500px;height:550px;padding:10px 5px 0px 5px;"
            closed="true" modal="true" buttons="#dlg-buttons_stud" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <table id="dg_add_student_2_group" class="easyui-datagrid" style="width:100%;height:95%"
        method="get" rownumbers="true" fitColumns="true" singleSelect="true" sortName="GROUP_NAME" sortOrder="asc" striped=true>

        <thead>
        <tr>            
            <th field="ID" width="5" hidden="true">ID</th>
            <th field="GROUP_NAME" width="80" sortable="true">������������ ������</th>
            <th field="LANGUAGE" width="50" sortable="true">����/����</th>
            <th field="NAME_PROGRAMM" width="60" sortable="true">���������</th>                                    
        </tr>
        </thead>
        </table>        
    </div> 
    <div id="dlg-buttons_stud">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="add_stud_2_group()" style="width:100px">���������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_add_student_2_group').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� �������� �������� � ������ -->
	
	 <!-- ����� ���������� ������� � �������� -->    
    <div id="dlg_add_pay_2_student" class="easyui-dialog" style="width:330px;height:470px;padding:10px 1px;"
            closed="true" modal="true" buttons="#dlg-buttons_pay" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">���������� �������</div>
        <form id="fm_pay" novalidate>
           <div class="fitem" style="margin-bottom:20px;">
               	<label>����� ����� �� ������� ������:</label>
               	<span id="sum_debt" style="font-weight: bold;"></span>
           	</div>
           <div class="fitem">
                <hr>
                </div>
           <div class="fitem">
               	<label>����� ������� (&#8381;):</label>
               	<input id="SUM_PAY" name="SUM_PAY" class="easyui-numberbox" data-options="precision:2">
           	</div>
		   <div class="fitem">
               	<label>���� �������:</label>
               	<input id="DATE_PAY" name="DATE_PAY" class="easyui-datebox" data-options="required:true, formatter:myformatter, parser:myparser" missingMessage="������ ���� ���������� ���������">
	        </div>
		   <div class="fitem">
               	<label>��� ������:</label>
               	<input id="KIND_OPL" name="KIND_OPL" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'text', textField: 'text', url: 'get_kind_opl.cgi?SID=$SID', method: 'get'" missingMessage="������ ���� ���������� ���������">
           	</div>
           <div class="fitem">
               	<label>�������:</label>
               	<input name="NOTES_PAY" class="easyui-textbox" data-options="multiline:true" style="height:100px">
	        </div>           
            
            <input name="num_dg_stud" type="hidden" id="num_dg_stud" value="" />
               
        </form>
    </div>
    <div id="dlg-buttons_pay">
        <a id="but_pay" href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="add_pay()" style="width:100px">��</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_add_pay_2_student').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� ���������� ������� � �������� -->
	
	<!-- ����� ��������� ������� �������� -->    
    <div id="dlg_filter" class="easyui-dialog" style="width:350px;height:280px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">��������� �������</div>
        <form id="fm_filter" novalidate>
            <table>
                <tr>
                    <td><label><input id="BR" name="checkbox" type="checkbox" value="BRANCH" />������:</label></td>
                    <td><input name="BR" class="easyui-combobox BR" data-options="editable:false, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_branches.cgi?SID=$SID', method: 'get'"></td>
                </tr>
                <tr>
                    <td><label><input id="SRC_ABOUT_US" name="checkbox" type="checkbox" value="SOURCE_ABOUT_US" />������ � ��� ������:</label></td>
                    <td><input name="SRC_ABOUT_US" class="easyui-combobox SRC_ABOUT_US" data-options="editable:false, panelHeight:'auto', valueField: 'id', valueText: 'text', url: 'get_source_about_us.cgi?SID=$SID', method: 'get'"></input></td>
                </tr>   
                <tr>
                    <td><label><input id="SEX_STUD" name="checkbox" type="checkbox" value="SEX" />���:</label></td>
                    <td>
                    <select name="SEX_STUD" class="easyui-combobox SEX_STUD" style="width:150px;" data-options="editable:false, panelHeight:'auto'">
               	    <option>�</option>
                    <option>�</option>
                    </select>
                    </td>
                </tr>
                            
                <tr>
                    <td><label><input id="erase_filter" name="checkbox" type="checkbox" /><strong>����� �������:</strong></label></td>                                       
                </tr>
            </table>    
        </form>
    </div>
    <div id="dlg-buttons">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="doFilter()" style="width:100px">����������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_filter').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� ��������� ������� �������� -->
	
	<!--����������� ���� -->
    <div id="mm_summ" class="easyui-menu" style="width:290px;">
        <div data-options="iconCls:'icon-tip'" onclick="open_window_change_summ();"><strong>�������� ����� ��� ������</strong></div>        
    </div>
    <!--����� ����������� ���� -->
    
    <!-- ����� ��������� ����� ��� ������ -->    
    <div id="dlg_summ" class="easyui-dialog" style="width:330px;height:200px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons_summ" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">��������� ����� ��� ������:</div>
        <form id="fm_summ" novalidate>           
            <div class="fitem">
               	<label>����� ��� ������:</label>
               	<input id="CHANGE_SUM_PAY" name="CHANGE_SUM_PAY" class="easyui-numberbox" data-options="precision:2">
	        </div>
                           
                <input id="id_pay" name="id_pay" type="hidden" value="" />
                <input id="num_dogovor_stud" name="num_dogovor_stud" type="hidden" value="" />
                           	
        </form>
    </div>
    <div id="dlg-buttons_summ">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="set_new_summ()" style="width:100px">����������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_summ').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� ��������� ����� ��� ������ -->
	
	<!-- ����� ����������� �������� ����� �������� -->    
    <div id="dlg_move_student" class="easyui-dialog" style="width:750px;height:500px;padding:10px 5px 0px 5px;"
            closed="true" modal="true" buttons="#dlg-buttons_stud" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
            <div class="ftitle">����������� ����� ��������</div>                     
            <div class="fitem" style="margin-bottom: 30px;">
               	<label><b>������� ������:</b></label>
               	<span id="current_group" style="font-weight: bold; color: red;"></span><br />
               	<hr />
	        </div>
	        
               	<label style="font-weight: bold; color: blue; margin-top: 30px;">����� ������ ��� ��������:</label>                
            
        <table id="dg_move_student" class="easyui-datagrid" style="width:100%;height:70%"
        method="get" rownumbers="true" fitColumns="true" sortName="GROUP_NAME" sortOrder="asc" singleSelect="true" striped=true>

        <thead>
        <tr>
            <th field="ck_bx" checkbox="true"></th>
            <th field="ID" hidden="true">ID</th>            
            <th field="GROUP_NAME" width="150" sortable="true">������������ ������</th>
            <th field="GROUP_TYPE" width="130">��� ������</th>
            <th field="GROUP_PRICE" width="110">��������� ������./���.</th>
            <th field="COURSE_PRICE" width="80">��������� �����</th>                                    
        </tr>
        </thead>
        </table>        
    </div> 
    <div id="dlg-buttons_stud">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="move_stud_2_group()" style="width:110px">�����������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_move_student').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� ����������� �������� ����� �������� -->
	
	 <!--����������� ���� �������� �������� � �����-->
    <div id="mm" class="easyui-menu" style="width:250px;">
        <div data-options="iconCls:'icon-tip'" onclick="move_student()"><strong>��������� �������� � �����</strong></div>
    </div>
    <!--����� ����������� ���� �������� �������� � ����� -->
	
	<!-- ����� ���������� ������� ��� ������ -->    
    <div id="dlg_add_period_pay" class="easyui-dialog" style="width:330px;height:200px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons_add_period_pay" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">���������� ������� ������:</div>
        <form id="fm_add_period_pay" novalidate>           
            <div class="fitem">
               	<label>����� ��� ������:</label>
               	<input id="SUMM_PAY" name="SUMM_PAY" class="easyui-numberbox" data-options="precision:2">
	        </div>
                           
                <input id="num_dogovor_student" name="num_dogovor_student" type="hidden" value="" />
                           	
        </form>
    </div>
    <div id="dlg-buttons_add_period_pay">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="add_period_pay()" style="width:100px">��������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_add_period_pay').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� ���������� ������� ��� ������ -->
	
	<!-- ����� ����������� ������� �������� -->    
    <div id="dlg_student_orders" class="easyui-dialog" style="width:700px;height:550px;padding:10px 5px 0px 5px;"
            closed="true" modal="true" buttons="#dlg-buttons_orders" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <table id="dg_student_orders" class="easyui-datagrid" style="width:100%;height:95%"
        method="get" fitColumns="true" singleSelect="true" striped=true>

        <thead>
        <tr>            
            <th field="ID" width="40">� ������</th>
            <th field="OSNOVANIE" width="180">���������</th>
            <th field="SUMM_OPL" width="50">���������� �����</th>
            <th field="STATUS" width="50">��� �������</th>
            <th field="DATE_PAY" width="60">���� �������</th>
            <th field="ORDER_MADE" width="100">����� ��������</th>                                    
        </tr>
        </thead>
        </table>        
    </div> 
    <div id="dlg-buttons_orders">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_student_orders').dialog('close')" style="width:90px">�������</a>
    </div>
    <!-- ����� ����� ����������� ������� �������� -->
	
	
	<!-- ����� ����������� ������� ��������� ������ ���� -->    
    <div id="dlg_student_orders_past_academ" class="easyui-dialog" style="width:700px;height:550px;padding:10px 5px 0px 5px;"
            closed="true" modal="true" buttons="#dlg-buttons_orders_past_academ" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <table id="dg_student_orders_past_academ"></table>                
    </div> 
    <div id="dlg-buttons_orders_past_academ">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_student_orders_past_academ').dialog('close')" style="width:90px">�������</a>
    </div>
    <!-- ����� ����� ����������� ������� ��������� ������ ���� -->
	
	<!-- ����� ���������� ����������� ����������� -->    
    <div id="dlg_visited_event" class="easyui-dialog" style="width:480px;height:320px;padding:10px 1px;"
            closed="true" modal="true" buttons="#dlg-buttons_visited_event" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">�����������</div>
        <form id="fm_visited_event" novalidate>
           <div class="fitem">
               	<label>���� ���������:</label>
               	<input id="DATE_VISIT" name="DATE_VISIT" class="easyui-datebox" data-options="required:true, formatter:myformatter, parser:myparser" missingMessage="������ ���� ���������� ���������">
	        </div>        
           <div class="fitem">
               	<label>��� �����������:</label>
               	<input id="KIND_EVENT" name="KIND_EVENT" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_kind_events.cgi?SID=$SID', method: 'get'" missingMessage="������ ���� ���������� ���������">
           	</div>
           <div class="fitem">
               	<label>�����:</label>
               	<input id="FEEDBACK" name="FEEDBACK" class="easyui-textbox" data-options="multiline:true" style="height:100px">
	        </div>                      
            <input name="number_dog_st" type="hidden" id="number_dog_st" value="" />
        </form>
    </div>
    <div id="dlg-buttons_visited_event">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="saveEvent()" style="width:100px">��������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_visited_event').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� ���������� ����������� ����������� -->
	
	<!-- ����� ���������� ������������� ������� � �������� -->    
    <div id="dlg_add_pay_2_student_without_group" class="easyui-dialog" style="width:330px;height:470px;padding:10px 1px;"
            closed="true" modal="true" buttons="#dlg-buttons_pay_without_gr" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">���������� ������������� �������</div>
        <form id="fm_pay_without_gr" novalidate>
           <div class="fitem">
               	<label>����� ������� (&#8381;):</label>
               	<input id="SUM_PAY_WITHOUT_GR" name="SUM_PAY_WITHOUT_GR" class="easyui-numberbox" data-options="precision:2">
           	</div>
           <div class="fitem">
               	<label>���� �������:</label>
               	<input id="DATE_PAY_WITHOUT_GR" name="DATE_PAY_WITHOUT_GR" class="easyui-datebox" data-options="required:true, formatter:myformatter, parser:myparser" missingMessage="������ ���� ���������� ���������">
	        </div>
	   <div class="fitem">
               	<label>��� ������:</label>
               	<input id="KIND_OPL_WITHOUT_GR" name="KIND_OPL_WITHOUT_GR" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'text', textField: 'text', url: 'get_kind_opl.cgi?SID=$SID', method: 'get'" missingMessage="������ ���� ���������� ���������">
           	</div>
           <div class="fitem">
               	<label>��������� ������:</label>
               	<input id="OSNOVANIE_OPL" name="OSNOVANIE_OPL" class="easyui-textbox" data-options="required:true" missingMessage="������ ���� ���������� ���������">
	        </div>
           <div class="fitem">
               	<label>�������:</label>
               	<input id="NOTES_PAY_WITHOUT_GR" name="NOTES_PAY_WITHOUT_GR" class="easyui-textbox" data-options="multiline:true" style="height:100px">
	        </div>           
            
            <input name="num_dg_stud_without_gr" type="hidden" id="num_dg_stud_without_gr" value="" />
               
        </form>
    </div>
    <div id="dlg-buttons_pay_without_gr">
        <a id="but_pay_without_gr" href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="add_pay_without_gr()" style="width:100px">��</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_add_pay_2_student_without_group').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� ������������ ���������� ������� � �������� -->
	
	<!-- ����� ����������� ������� ��������� -->    
    <div id="window_student_feedback" class="easyui-dialog" style="width:700px;height:550px;padding:10px 5px 0px 5px;"
            closed="true" modal="true", buttons="#dlg-buttons_feedback_st" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">            
        <table id="dg_student_feedback"></table>   
    </div> 
    <div id="dlg-buttons_feedback_st">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#window_student_feedback').dialog('close')" style="width:90px">�������</a>
    </div>
    <!-- ����� ����� ����������� ������� ��������� --> 
	
	<!-- ����� ����������� ������� ������� ��������� -->    
    <div id="window_student_past_feedback" class="easyui-dialog" style="width:700px;height:550px;padding:10px 5px 0px 5px;"
            closed="true" modal="true", buttons="#dlg-buttons_past_feedback_st" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">            
        <table id="dg_student_past_feedback"></table>   
    </div> 
    <div id="dlg-buttons_past_feedback_st">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#window_student_past_feedback').dialog('close')" style="width:90px">�������</a>
    </div>
    <!-- ����� ����� ����������� ������� ������� ��������� -->   

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
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://localhost:6080');
         print "Set-Cookie: $cookies\n";
         $sess->delete();
         $sess->flush();
        }

#���������� SID � URL ������
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

__END__