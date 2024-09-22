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

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {
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
		
		<!-- �������� ������� "�����" -->
        <style>
        #blink-2{
        margin-left:20px;
        color: #000000;
        font-size: 24px;
        font-weight: 700;
        text-align: center;
        animation:blur .95s ease-out infinite;
        text-shadow:text-shadow: 0 0 5px #abc, 0 0 7px #abc;
        }
 
        \@keyframes blur{
        from{
        text-shadow:0px 0px 10px #fff,
        0px 0px 10px #fff, 
        0px 0px 25px #fff,
        0px 0px 25px #fff,
        0px 0px 25px #fff,
        0px 0px 25px #fff,
        0px 0px 25px #fff,
        0px 0px 25px #fff,
        0px 0px 50px #fff,
        0px 0px 50px #fff,
        0px 0px 50px #7B96B8,
        0px 0px 150px #7B96B8,
        0px 10px 100px #7B96B8,
        0px 10px 100px #7B96B8,
        0px 10px 100px #7B96B8,
        0px 10px 100px #7B96B8,
        0px -10px 100px #7B96B8,
        0px -10px 100px #7B96B8;}
        }
        </style>
        <!-- **************************** -->
		
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
       //fio: \$('#fio').val(),
	   fio: \$('#fio').textbox('getText'),
       //n_dogovor: \$('#n_dogovor').val()
	   n_dogovor: \$('#n_dogovor').numberbox('getText')
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
       url: 'get_student_detail_archive.cgi?num_dog='+row.Num_dogovor+'&SID=$SID',
       showGroup: true,
       showHeader: false,
       scrollbarSize: 0
       });
       //////////////////////////////////////////
       
       //��������� � ��������� ������� �� ��������       
       \$('#hs').datagrid({
       method:'get',
       url:'get_student_history_archive.cgi?num_dog='+row.Num_dogovor+'&SID=$SID',
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
       url:'get_docum_in_student_archive.cgi?id_z2='+row.Num_dogovor+'&SID=$SID',
       columns:[[
                 {field:'ID',title:'ID', hidden:true},
                 {field:'TYPE_DOC',title:'��� ���������'},
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
       url:'get_group_in_student_archive.cgi?id_z3='+row.Num_dogovor+'&SID=$SID',
       columns:[[
                 {field:'GROUP_ID'},
                 {field:'GROUP_NAME',title:'������������ ������'},                 
                 {field:'LANGUAGE',title:'����'},
                 {field:'KIND_PROGRAMM',title:'������������ ���������'}
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
       url:'get_pays_in_student_archive.cgi?id_z4='+row.Num_dogovor+'&SID=$SID',
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
         var ss = [];
         ss.push(row.Num_dogovor);
         \$.ajax({            
         type: 'GET',
         traditional: true,
         url: 'get_group_name_archive.cgi?SID=$SID',
         data: {'data':ss},            
         success: function(res) {
                                  \$('#group').text('��.: '+res.result); //��������� ������������ � ��������� �����                                  
                                  \$('#p').show();
                                  \$('#p').progressbar({
                                                         value: res.proc
                                                      });
                                  \$('#paid').text('�������� ��������: '+res.summ_debt+' ���.'); 
                                  \$('#sum_debt').text(res.summ_debt_curr_per+' ���.'); 
                                                                    
                                },
         error: function() {
                             \$('#group').text('');
                             \$('#p').hide();
                             \$('#paid').text('');     
                             \$('#sum_debt').text('');                                                      
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
                    {field:'PUPILS_NUM_DOGOVOR',title:'Num_dog',width:20, hidden:true},
                    {field:'UUID',title:'uuid',width:20, hidden:true},
                    {field:'PERIOD',title:'������ ��������',width:200}                                                                                 
                ]],                
                method: 'get',
                url:'get_student_past_academ_period_archive.cgi?SID=$SID&number_dog='+row.Num_dogovor,
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
                    url:'get_student_past_academ_period_gr_archive.cgi?SID=$SID',
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
                        url:'get_student_past_academ_period_doc_archive.cgi?SID=$SID',
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
                            url:'get_student_past_academ_period_pays_archive.cgi?SID=$SID',
                        }
                        
                    }
                }
            }
        };     
        
        \$('#past_academ_years').datagrid({title:'������ ������� ������. �����'}).datagrid('subgrid', conf);
       
       ///////////////////////////////////////////////////////////////////////////
       
          
        //���������� ��������� ��� ����������� �� ���������. �������� ������� ����������� ��������
	    scheduler.clearAll();
	    scheduler.load("get_calendar_events_students_archive.cgi?SID=$SID"+"&num_dog="+row.Num_dogovor,"json");		
	    scheduler.updateView();   
        ///////////////////////////////////////////////////////////////////
		
		
		//��������� � ������� ������ ���������� ���������� ���������
        \$('#visited_events').datagrid({       
        title: '���������� �����������:',
        method:'get',
        showFooter: false,
        scrollbarSize: 0,
        striped: true,
        border: false,
        singleSelect: true,
        url:'get_visited_events_archive.cgi?id_z5='+row.Num_dogovor+'&SID=$SID',
        columns:[[                
                 {field:'DATE_VISIT',title:'���� ���������', width:100},                 
                 {field:'KIND_EVENT',title:'��� �����������', width:200},
                 {field:'FEEDBACK',title:'�����', width:200}                 
               ]]
        });       
        //////////////////////////////////////////
		
		//��������� � ������� ������ ������������ �����
        \$('#wp').datagrid({       
        title: '������������ ������',
        method:'get',
        showHeader: true,
        showFooter: false,
        scrollbarSize: 0,
        striped: true,
        border: false,
        singleSelect: true,
        url:'get_pays_without_group_archive.cgi?id_zwp='+row.Num_dogovor+'&SID=$SID',
        columns:[[                                 
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
        
        <script>//������� ��������� ������ 
       \$(function(){
               
        \$('#list_of_groups').datagrid({
	rowStyler: function(index,row){
			return 'background-color:#e5f1ff;'; // return inline style
			          }
        });
        
        });
        </script>
       
        
        <script> //����������� ������ �� ������� Enter
        \$(document).ready(function(){
	var t = \$('#fio');
	var n = \$('#n_dogovor');
	
	////////////
	t.textbox('textbox').bind('keydown', function(e){
	   if (e.keyCode == 13) 
	   { 
	      doSearch();
	   }
	});	
	
	///////////
	n.numberbox('textbox').bind('keydown', function(e){
	   if (e.keyCode == 13) 
	   { 
	      doSearch();
	   }
	});
        })
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
                        url:'get_detail_groups_archive.cgi?SID=$SID&id_str='+row_stud.Num_dogovor,
                        method: 'get',
                        fitColumns:true,
                        singleSelect:true,
                        rownumbers:true,
                        loadMsg:'',
                        height:'60px',
                        columns:[[
                            {field:'START_DATE',title:'���� ������',width:90},
                            {field:'END_DATE',title:'���� ���������',width:100,align:'right'},
                            {field:'PRICE_COURSE',title:'��������� �����',width:100,align:'right'},
                            {field:'BEGIN_STUDY',title:'������ ��������',width:110,align:'right'}
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
        
        
        })
        </script>
		
		<script>
        function open_window_move_students(){            
          \$('#dlg_move_students_2_archive').window('open').dialog('center').dialog('setTitle','��������');
          \$('#dg_move_st').datagrid({url: 'get_students_4_archive.cgi?SID=$SID'});                                
        }
        </script>
        
        <script> //����� ���-�� ���������� ���������
        \$(function(){
        \$('#dg_move_st').datagrid({
        onSelect:function(index){
                                 var rows = \$('#dg_move_st').datagrid('getSelections');
                                 \$('#lb_stud_arch').text('���-�� ��������� ���������:'+rows.length);        
                                },
        onUnselect:function(index){
                                 var rows = \$('#dg_move_st').datagrid('getSelections');
                                 \$('#lb_stud_arch').text('���-�� ��������� ���������:'+rows.length);        
                                },
        onSelectAll:function(index){
                                 var rows = \$('#dg_move_st').datagrid('getSelections');
                                 \$('#lb_stud_arch').text('���-�� ��������� ���������:'+rows.length);        
                                },
        onUnselectAll:function(index){
                                 var rows = \$('#dg_move_st').datagrid('getSelections');
                                 \$('#lb_stud_').text('���-�� ��������� ���������:'+rows.length);        
                                }
                        });
                });
        </script>
        
        <script>
        function move_students_2_arch(){                 
            \$.messager.confirm('��������','�� �������, ��� ���������� ��������� ��������� � �����?',function(r){
            if (r){
                     var ss = [];
                     var rows = \$('#dg_move_st').datagrid('getSelections');
                     if (rows){
                                 for(var i=0; i<rows.length; i++){
                                     var row = rows[i];
                                     ss.push(row.Num_dogovor);
                                 }     
                   
                     \$.ajax({            
                     type: 'GET',
                     traditional: true,
                     url: 'move_students_2_archive.cgi?SID=$SID',
                     data: {'dat':ss},
                     success: function(res) {\$.messager.alert('����������',res.result,'info'); if (res.result=="������� ���������� ������!") {\$('#dlg_move_students_2_archive').dialog('close');\$('#dg').datagrid('reload');}},
                     error: function() {alert("did not work");}
                     });            
                     }                     
                   }                   
              });
        }
        </script>
		
		<script>
        function show_orders_past_academ(){
        var row_st1 = \$('#past_academ_years').datagrid('getSelected');        
            if (row_st1){
            \$('#dlg_student_orders_past_academ').window('open').dialog('center').dialog('setTitle','������ ��������');
            \$('#dg_student_orders_past_academ').datagrid({url: 'get_student_orders_past_academ_archive.cgi?SID=$SID&n_dog='+row_st1.PUPILS_NUM_DOGOVOR+'&uuid='+row_st1.UUID});
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
             if (row_num_dog){                
             \$('#window_student_feedback').window('open').dialog('center').dialog('setTitle','����� ��������');
             \$('#dg_student_feedback').datagrid({url: 'get_student_feedback_archive.cgi?SID=$SID&nm_dogovor='+row_num_dog.Num_dogovor});               }
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
                   {field:'TOPIC',title:'����',width:150},
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
        url:'get_visits_stud_archive.cgi?id_vis='+r_num_dg.Num_dogovor+'&SID=$SID',
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
        url:'get_homework_stud_archive.cgi?id_hw='+r_num_dg.Num_dogovor+'&SID=$SID',
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
             url:'get_past_visits_stud_archive.cgi?uuid_past_vis='+row_past_visits.UUID+'&SID=$SID',
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
             url:'get_past_homework_stud_archive.cgi?uuid_past_hw='+row_past_visits.UUID+'&SID=$SID',
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
             \$('#dg_student_past_feedback').datagrid({url: 'get_student_past_feedback_archive.cgi?SID=$SID&uuid_past_feedback='+row_past_per.UUID});               }
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
        <body class="easyui-layout" onload="init();">
        <!--������� DIV - ��������� -->
        <div data-options="region:'north',border:false" style="height:100px;background:#f0993c;padding:10px;"><h1 class="shd">@name_org</h1>
        <!--DIV � ������� ����� ������ ������-->
HTML
     
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
         <div title="������">
            
            <!-- ����� ������ ����� � ������� �������� �������-->
            <table id="list_of_groups"></table>
            <!-- ����� ����� ������ ����� � ������� �������� ������� -->
            
         </div>
         <div title="�������"">
         
         <!--������� �������� ������, ������ ��������� ����� � ������� ���������� �������-->
         <div style="margin-bottom: 10px;">
          <span id="group" style="font-weight: bold; float: left;"></span>
          <div id="p" style="width:auto; height:15px; bold;"></div> 
          </br>
          <span id="paid" style="font-weight: bold;"></span>         
         </div>         
         <!--����� ������� �������� ������, ������ ��������� ����� � ������� ���������� �������-->
         
         <!-- ����� ������ ����� ��������-->
         <table id="list_of_pays"></table>
         <!-- ����� ����� ������ ����� �������� -->
            
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
            <a href="#" class="easyui-linkbutton" iconCls="icon-list" plain="true" onclick="show_feedback()">�������� ������</a>           
          </div>       
          
         </div>
		 
         <div title="���������">                        
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
           <table id="wp" style="width:100%"></table>
         </div>
		 
        </div>
        <!-- ����� ������ TABS -->

        </div>
        <!-- ����� ������ DIV ������ ����������� -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->

        <!-- ����������� DIV -������� ������� -->
        <div data-options="region:'center',title:'������� ������� - ����� ���������. ������������: $formLogin'">

        <table id="dg" title="<span id='blink-2' style='font-size:18pt'>�����</span>" class="easyui-datagrid" style="width:100%;height:95%"
        method="get"
        url="get_students_archive.cgi?SID=$SID"
        toolbar="#tb, #toolbar"
        rownumbers="true" fitColumns="true" singleSelect="true" pagination="true" sortName="Num_dogovor" sortOrder="asc">

        <thead>
        <tr>
            <th field="Num_dogovor" width="15" sortable="true">�������</th>
            <th field="FIO" width="167" sortable="true">���</th>
            <th field="MOBILE_PHONE" width="30">���.���</th>
            <th field="HOME_PHONE" width="20">���.���</th>
            <th field="MARK_FROM_ZAYAV" width="2" hidden="true">MARK_FROM_ZAYAV</th>
        </tr>
        </thead>
        </table>
        <div id="toolbar">
        <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="open_window_move_students()">��������� ��������� � �����</a>
        </div>

        <!-- ������ ������ -->
        <div id="tb" style="padding:3px">
             <span>����� �� ���:</span>
             <input id="fio" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
             <span>����� �� ��������:</span>
             <input id="n_dogovor" class="easyui-numberbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">             
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
    
    
    <!-- ���� ����������� ������������ ��������� -->
    <div id="tied_doc" class="easyui-window" title="���������� ���������" style="width:100%;height:100%;"
        data-options="iconCls:'icon-print',modal:true,closed:true">
        <textarea name="TEXT_OF_DOCUMENT" id="TEXT_OF_DOCUMENT"></textarea>               
    </div>
    <!-- ����� ���� ����������� ������������ ��������� -->
	
	 <!-- ����� �������� ��������� � ����� -->    
    <div id="dlg_move_students_2_archive" class="easyui-dialog" style="width:450px;height:500px;padding:10px 5px 0px 5px;"
            closed="true" modal="true" buttons="#dlg-butt_stud_arch" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <span id="lb_stud_arch" style="float:left; font-weight: bold; margin-bottom:10px;">���-�� ��������� ���������:</span>
        <table id="dg_move_st" class="easyui-datagrid" style="width:100%;height:75%"
        method="get" fitColumns="true" sortName="FIO" sortOrder="asc" striped=true>

        <thead>
        <tr>
            <th field="ck_bx" checkbox="true"></th>
            <th field="Num_dogovor" width="40">� ��������</th>
            <th field="FIO" width="170" sortable="true">��� ��������</th>
            <th field="DATE_OF_BORN" width="80">���� ��������</th>                                    
        </tr>
        </thead>
        </table>        
    </div> 
    <div id="dlg-butt_stud_arch">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="move_students_2_arch()" style="width:100px">���������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_move_students_2_archive').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� �������� ��������� � ����� -->
    
	<!-- ����� ����������� ������� ��������� ������ ���� -->    
    <div id="dlg_student_orders_past_academ" class="easyui-dialog" style="width:700px;height:550px;padding:10px 5px 0px 5px;"
            closed="true" modal="true" buttons="#dlg-buttons_orders_past_academ" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <table id="dg_student_orders_past_academ">                
    </div> 
    <div id="dlg-buttons_orders_past_academ">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_student_orders_past_academ').dialog('close')" style="width:90px">�������</a>
    </div>
    <!-- ����� ����� ����������� ������� ��������� ������ ���� -->
	
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