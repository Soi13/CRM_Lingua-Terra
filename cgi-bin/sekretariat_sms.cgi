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
my $SMS_SEKRETARIAT=$sess->param('SMS_SEKRETARIAT');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

    if ($SMS_SEKRETARIAT==1) #������� ����� �� ������ ������������ � ������ "���".
    {
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

        #��������� ������� ��� ������� � ���.
        my $cgi=CGI->new;
        my @res;

        #���������� ���� �� ������ � �� � ������ � ������ ��� �����
        my $data;
        my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth=$dbh->do("SET NAMES 'cp1251'");
        my $sql="select LOGIN, PASSW from sms_gate";
        $sth=$dbh->prepare($sql);
        $sth->execute();
        my @row_gate = $sth->fetchrow_array;
        #################################################

        #�������� ��������������� ������ � ���-�����
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
        if ($bal->{amount}) { $balance="(������: ".$bal->{amount}." ���.)"; } else { $balance=""; }


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
	   
	   <script>//��������� Keyboard Navigation
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
       
       <script> //������� ���-�� ��������� ��������
       \$(function(){      
        \$('#sms_text').textbox({
	inputEvents:\$.extend({},\$.fn.textbox.defaults.inputEvents,{
		keyup:function(e){
			var st=\$('#sms_text').textbox('getText');
			var res=st.length;
			var cnt_sms=parseInt(res/70)+1;			
			\$('#cnt_symbol').text("������� "+res+" ��������, ���-�� ���: "+cnt_sms);			
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
			\$('#cnt_symbol_teacher').text("������� "+res1+" ��������, ���-�� ���: "+cnt_sms1);			
		    }
	      })
        })
        ////////////////////////////////////
		
                  });
        </script>
        
        <script>
        function open_window_select_stud(){
           \$('#dlg_select_student').window('open').dialog('center').dialog('setTitle','����� ��������� ��� �������� ���');
           \$('#dg_select_student').datagrid({url: 'get_students_4_send_sms.cgi?SID=$SID'});            
        }
		/////////////////////////////////////////////
		
		function open_window_select_teachers(){
           \$('#dlg_select_teacher').window('open').dialog('center').dialog('setTitle','����� �������������� ��� �������� ���');
           \$('#dg_select_teachers').datagrid({url: 'get_teachers_4_send_sms.cgi?SID=$SID'});            
        }
        </script>
        
        <script> //����� ���-�� ���������� ���������
        \$(function(){
        \$('#dg_select_student').datagrid({
        onSelect:function(index){
                                 var rows = \$('#dg_select_student').datagrid('getSelections');
                                 \$('#lb_stud').text('���-�� ��������� ���������:'+rows.length);        
                                },
        onUnselect:function(index){
                                 var rows = \$('#dg_select_student').datagrid('getSelections');
                                 \$('#lb_stud').text('���-�� ��������� ���������:'+rows.length);        
                                },
        onSelectAll:function(index){
                                 var rows = \$('#dg_select_student').datagrid('getSelections');
                                 \$('#lb_stud').text('���-�� ��������� ���������:'+rows.length);        
                                },
        onUnselectAll:function(index){
                                 var rows = \$('#dg_select_student').datagrid('getSelections');
                                 \$('#lb_stud').text('���-�� ��������� ���������:'+rows.length);        
                                }
                        });
		///////////////////////////////////////////////////////
		
		\$('#dg_select_teachers').datagrid({
        onSelect:function(index){
                                 var rows1 = \$('#dg_select_teachers').datagrid('getSelections');
                                 \$('#lb_teachers').text('���-�� ��������� ��������������:'+rows1.length);        
                                },
        onUnselect:function(index){
                                 var rows1 = \$('#dg_select_teachers').datagrid('getSelections');
                                 \$('#lb_teachers').text('���-�� ��������� ��������������:'+rows1.length);        
                                },
        onSelectAll:function(index){
                                 var rows1 = \$('#dg_select_teachers').datagrid('getSelections');
                                 \$('#lb_teachers').text('���-�� ��������� ��������������:'+rows1.length);        
                                },
        onUnselectAll:function(index){
                                 var rows1 = \$('#dg_select_teachers').datagrid('getSelections');
                                 \$('#lb_teachers').text('���-�� ��������� ��������������:'+rows1.length);        
                                }
        });
        ///////////////////////////////////////////////////////////////////////////////////////
						
        });
        </script>
        
       <script>//��������� ������� ��� ����� ������ �������� ��� �������� ���
       function doFilter_4_send_sms(){
       
       //��������, ������ ���� �� ���� �������� ����������
       if((!\$("#radio_DATE_OF_DOGOVOR").prop("checked")) && (!\$("#radio_KIND_PROG").prop("checked")) && (!\$("#radio_erase_filter_tie").prop("checked"))) {
	    \$.messager.alert('��������','�� ������ �������� ����������!','warning');
	    return;
        }        
               
       ///////////////////
       if(\$("#radio_DATE_OF_DOGOVOR").prop("checked")) { 
              \$('#dg_select_student').datagrid('load',{
              date_of_dogovor_from: \$('#DATE_OF_DOGOVOR_FROM').datebox('getValue'),
              date_of_dogovor_to: \$('#DATE_OF_DOGOVOR_TO').datebox('getValue')             
              });
              \$('#lb_tie').text('���������� ������ �� "���� ��������"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_KIND_PROG").prop("checked")) { 
              \$('#dg_select_student').datagrid('load',{
              kind_prog: \$('#KIND_PROG').combobox('getValue'),
              });
              \$('#lb_tie').text('���������� ������ �� "���������"');
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
 
       \$('#fm_filter_4_send_sms').form('clear'); \$('#dlg_filter_4_send_sms').dialog('close'); //��������� � ����� ���������� � ������� ����
 
       }
       </script>//����� ������� ��������� ������� ��� ����� ������ �������� ��� �������� ���       
       
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
            {field:'Num_dogovor',title:'���������',width:50},	   
	        {field:'FIO',title:'���',width:230},
			{field:'MOBILE_PHONE',title:'���.���.',width:120},
			{field:'action',title:'Action',width:80,align:'center',	formatter:function(value,row,index){return '<a href="javascript:void(0)" onclick="deleterow(this)">�������</a>'}}
		   ]]
		});
		////////////////////////////
		
		\$('#dg_selected_teachers').datagrid({
	    width:'100%',
	    height:'100%',
	    singleSelect:true,
	    showHeader:false,
	    columns:[[	               
	        	{field:'FIO',title:'���',width:250},
			{field:'PHONE',title:'���.���.',width:120},
			{field:'action',title:'Action',width:80,align:'center',	formatter:function(value,row,index){return '<a href="javascript:void(0)" onclick="deleterow_tech(this)">�������</a>'}}
		   ]]
	    });
	    ///////////////////			
	    });
		
	function getRowIndex(target){
	        var tr = \$(target).closest('tr.datagrid-row');
		return parseInt(tr.attr('datagrid-row-index'));
	}
	
	function deleterow(target){
		\$.messager.confirm('��������','�� �������?',function(r){
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
		\$.messager.confirm('��������','�� �������?',function(r){
		if (r){
			\$('#dg_selected_teachers').datagrid('deleteRow', getRowIndex_tech(target));
	              }
		});
	}	
	</script>
	
	<script> //������� ������� ������ ��������� ��� ��������
	function clear_addr(){
              \$.messager.confirm('��������','�� �������, ��� ���������� �������� ������ ��������� ��� ��������?',function(r){
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
	
	<script> //������� ������� ������ �������� ��� ��������
	function clear_addr_teachers(){
              \$.messager.confirm('��������','�� �������, ��� ���������� �������� ������ �������������� ��� ��������?',function(r){
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
            success: function(res) {\$.messager.alert('����������',res.result,'info');},
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
            success: function(res) {\$.messager.alert('����������',res.result,'info');},
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
             \$('#lb').text('���������� ������ ��: '+v);
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
                     incorrect_numbers.push('<br />'+fio_debt_today); //��������� ������ ��� ��������� ������� �� ����� ���������� ���, �.�. � ��� �� ���������� �����
                     continue;
                }
                
                ss_debts_today.push(num_phone_debt_today, summ_debt_today, dog_debt_today); //��������� ������ ����������� �������� ��������� � �� ������� ����� ��� �������� �� � ���
            }
            
                        
            if (incorrect_numbers.length>0)
            {
               status_message='������������� ��������� �������� ��������� �� ����� �� ������� ���������� ��� �������������� ���������� ������!<b>'+ incorrect_numbers +'</b><br />���������� �������� ��� ��������?';            
            }
            else
            {
               status_message='�� �������, ��� ���������� �������� ��������?';
            }
            
            \$.messager.confirm('��������', status_message, function(r){
                    if (r){
                               \$.ajax({            
                               type: 'GET',
                               traditional: true,
                               url: 'send_sms_debts_today.cgi?SID=$SID',
                               data: {'data':ss_debts_today},
                               success: function(res) {\$.messager.alert('����������',res.result,'info');},
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
           \$('#lb_month').text('�������� ��: '+v);
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
                     incorrect_numbers_month.push('<br />'+fio_debt_month); //��������� ������ ��� ��������� ������� �� ����� ���������� ���, �.�. � ��� �� ���������� �����
                     continue;
                }
                
                ss_debts_month.push(num_phone_debt_month, summ_debt_month, dog_debt_month); //��������� ������ ����������� �������� ��������� � �� ������� ����� ��� �������� �� � ���
            }
            
                        
            if (incorrect_numbers_month.length>0)
            {
               status_message_month='������������� ��������� �������� ��������� �� ����� �� ������� ���������� ��� �������������� ���������� ������!<b>'+ incorrect_numbers_month +'</b><br />���������� �������� ��� ��������?';            
            }
            else
            {
               status_message_month='�� �������, ��� ���������� �������� ��������?';
            }
            
            \$.messager.confirm('��������', status_message_month, function(r){
                    if (r){
                               \$.ajax({            
                               type: 'GET',
                               traditional: true,
                               url: 'send_sms_debts_month.cgi?SID=$SID',
                               data: {'data':ss_debts_month},
                               success: function(res) {\$.messager.alert('����������',res.result,'info');},
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
                    \$('#lb_dg').text('��� ���������� � ����� ��� ��������� � ��� ����������� �����: %1% - ���������, %2% - ���.');
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
        <!-- <div data-options="region:'east',split:true,title:'�����������'" style="width:30%;padding:1px;"> -->
        <!-- </div> -->
        <!-- ����� ������ DIV ������ ����������� -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->

        <!-- ����������� DIV -������� ������� -->
        <div data-options="region:'center',title:'������� ������� - ��� �������� $balance. ������������: $formLogin'">
        
           <!-- ������ ����� ��� ����������� ��� �������� --> 
           <div id="tabs_sms" class="easyui-tabs" data-options="pill:true, justified:true" style="width:100%;height:100%">
              
              <div title="������� ��������" style="padding:10px">
              
                 <!-- ����������� layout ��� �������� ��� --> 
                 <div class="easyui-layout" style="width:100%;height:100%;">
                    
                    <!-- ��������� DIV ������ ����������� -->
                   <div data-options="region:'east',split:true" title="������ ��������� ���������" style="width:30%;">                   
                     
                     <table id="dg_selected_students"></table>
                    
                   </div>
                   <!-- ����� ��������� DIV ������ ����������� -->
             
                   <!-- �������������� DIV -������� ������� -->
                   <div data-options="region:'center'" title="������� �������� ���">
                      
                      <div style="margin:10px 0 0 10px;">
                        <a href="#" class="easyui-linkbutton" style="width:150px;" iconCls="icon-man" onclick="open_window_select_stud()">����� ���������</a>
                        <br />
                        <div style="margin-top:20px;">
                          <input id="sms_text" class="easyui-textbox" data-options="prompt:'������� ����� ��� ���������...'" multiline="true" style="width:80%;height:120px;">
                        </div>
                        <br />
                        <div style="margin-top:-10px;">
                          <span id="cnt_symbol" style="font-weight: bold;">������� 0 ��������, ���-�� ���: 1</span>
                        </div>
						<label>������������ ��������� � ��� � ������ ���?:</label>                        
               	        <input id="USE_DOG_FIO" name="USE_DOG_FIO" class="easyui-switchbutton" value="1" data-options="onText:'��',offText:'���'">
               	        <br />
               	        <span id="lb_dg" style="float:left; color: #F00; font-weight: bold;"></span>
               	        <br />               	        
                        <a href="#" class="easyui-linkbutton" style="width:150px;" iconCls="icon-sms" onclick="send_sms()">���������</a>
                        <a href="#" class="easyui-linkbutton" style="width:170px;" iconCls="icon-del_list" onclick="clear_addr()">�������� ��������</a>                        
                      </div>
                   
                   
                   </div>
                   <!-- ����� �������������� DIV -������� ������� -->
                 
                 </div>
                 <!-- ����� ����������� layout ��� �������� ��� --> 
              
              </div>
              
              <div title="�������� ���������" style="padding:10px">
			  
			      <!-- ������ ����� ��� ����������� �������� ��������� --> 
                  <div id="tabs_debts" class="easyui-tabs" data-options="pill:true, justified:true, fit:true" style="width:100%;height:100%">
                      
                      <div title="�������� �� �������" style="padding:10px">
                      
                         <a href="#" class="easyui-linkbutton" style="width:150px; margin-bottom:10px;" iconCls="icon-document" onclick="build_debts()">������������</a>
                         <div style="margin-left:10px; margin-bottom:5px; color: #F00; font-weight: bold;">
                         <label>��������� ���������������� �� ��������:</label>
               	         <input id="INDIVIDUAL_COMMON" name="INDIVIDUAL_COMMON" class="easyui-switchbutton" value="1" data-options="onText:'��',offText:'���'">              	        
                         </div>                         
                         
                         <table id="dg_debts" title="�������� �� �������" class="easyui-datagrid" style="width:100%;height:85%"
                         method="get"                         
                         toolbar="#tb"
                         rownumbers="true" fitColumns="true" singleSelect="true" sortName="nm_dg" sortOrder="asc" showFooter="true">

                         <thead>
                         <tr>
                             <th field="nm_dg" width="20" sortable="true">�������</th>
                             <th field="fio" width="167" sortable="true">���</th>
                             <th field="mobile_phone" width="50">���.�������.</th>                             
                             <th field="summ" width="30">�����</th>            
                             <th field="name" width="30"></th>
                             <th field="count" width="30"></th>            
                         </tr>
                         </thead>
                         </table>        
              
                         <!-- ������ ������ -->
                         <div id="tb" style="padding:3px">
                         <span>����� �� ���:</span>
                         <input id="fio" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
                         <span>����� �� ��������:</span>
                         <input id="n_dogovor" class="easyui-numberbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">             
                         <span>����� �� �������������:</span>
                         <input id="TEACHER_ID" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_teacher_4_lessons.cgi?SID=$SID', method: 'get', icons:[{iconCls:'icon-clear', handler: function(e){var v = \$(e.data.target).combobox('clear');} }]   ">
                         <a href="#" id="fd" class="easyui-linkbutton" plain="false" disabled="true" onclick="search_data()" style="border-radius:5px; width:100px;">������</a>
                         <span id="lb" style="color: #F00; font-weight: bold;"></span>                                               
                         </div>
                         <!-- ����� ������ ��� ������ -->
                         <br />
                         <a href="#" class="easyui-linkbutton" style="width:350px; margin-left:40%;" iconCls="icon-sms" onclick="send_sms_debts_today()">���������</a>
                         
                      
                      </div>
                      
                      <div title="�������� �� �����" style="padding:10px">   

                        <table id="dg_debts_month" title="�������� �� �����" class="easyui-datagrid" style="width:100%;height:90%"
                        method="get"
                        url=""
                        toolbar="#tb_month"
                        rownumbers="true" fitColumns="true" singleSelect="true" sortName="nm_dg" sortOrder="asc" showFooter="true">
                        
                        <thead> 
                         <tr>
                           <th field="nm_dg" width="20" sortable="true">�������</th>
                           <th field="fio" width="167" sortable="true">���</th>
                           <th field="mobile_phone" width="50">���.�������.</th>                                                          
                           <th field="summ" width="30">�����</th>            
                           <th field="name" width="30"></th>
                           <th field="count" width="30"></th>            
                         </tr>
                        </thead> 
                        </table>        
              
                        <!-- ������ ������ -->
                        <div id="tb_month" style="padding:3px">
                        <div style="margin-top:5px; margin-bottom:5px">
                        <span>������������ ��������� �� �����:</span>
                        <select id="month" class="easyui-combobox" name="month" style="width:100px">
                        <option value="1">������</option>
                        <option value="2">�������</option>
                        <option value="3">����</option>
                        <option value="4">������</option>
                        <option value="5">���</option>
                        <option value="6">����</option>
                        <option value="7">����</option>
                        <option value="8">������</option>
                        <option value="9">��������</option>
                        <option value="10">�������</option>
                        <option value="11">������</option>
                        <option value="12">�������</option>             
                        </select>
						<input id="year" name="year" class="easyui-combobox" data-options="editable:false, valueField:'id',textField:'name'">
                        <span>    �� �������������:</span>
                        <input id="TEACHER_ID_month" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_teacher_4_lessons.cgi?SID=$SID', method: 'get', icons:[{iconCls:'icon-clear', handler: function(e){var v = \$(e.data.target).combobox('clear');} }]   ">
                        <a href="#" class="easyui-linkbutton" plain="false" onclick="make_report()" style="border-radius:5px; width:100px;">������������</a>             
                        <span id="lb_month" style="color: #F00; font-weight: bold;"></span>    
                        <br />
                        <div style="margin-top:10px; margin-left:10px; color: #F00; font-weight: bold;">
                           <label>��������� ���������������� �� ��������:</label>
               	           <input id="INDIVIDUAL" name="INDIVIDUAL" class="easyui-switchbutton" value="1" data-options="onText:'��',offText:'���'">              	        
                        </div>						
                        </div>                       
                        </div>
                        <!-- ����� ������ ��� ������ -->
                        <br />
                        <a href="#" class="easyui-linkbutton" style="width:350px; margin-left:40%;" iconCls="icon-sms" onclick="send_sms_debts_month()">���������</a>   
					  
                      </div>
                      
                  </div>
                  <!-- ����� ������ ����� ��� ����������� �������� ��������� --> 
			  
              </div>
              
              <div title="�������� ��������������" style="padding:10px">
			  
                    <!-- ����������� layout ��� �������� ��� --> 
                    <div class="easyui-layout" style="width:100%;height:100%;">
                    
                    <!-- ��������� DIV ������ ����������� -->
                    <div data-options="region:'east',split:true" title="������ ��������� ��������������" style="width:30%;">                   
                     
                     <table id="dg_selected_teachers"></table>
                    
                    </div>
                    <!-- ����� ��������� DIV ������ ����������� -->
             
                   <!-- �������������� DIV -������� ������� -->
                   <div data-options="region:'center'" title="������� �������� ��� ��� ��������������">
                      
                      <div style="margin:10px 0 0 10px;">
                        <a href="#" class="easyui-linkbutton" style="width:150px;" iconCls="icon-man" onclick="open_window_select_teachers()">����� ���������</a>
                        <br />
                        <div style="margin-top:20px;">
                          <input id="sms_text_teacher" class="easyui-textbox" data-options="prompt:'������� ����� ��� ���������...'" multiline="true" style="width:80%;height:120px;">
                        </div>
                        <br />
                        <div style="margin-top:-10px;">
                          <span id="cnt_symbol_teacher" style="font-weight: bold;">������� 0 ��������, ���-�� ���: 1</span>
                        </div>
                        <a href="#" class="easyui-linkbutton" style="width:150px;" iconCls="icon-sms" onclick="send_sms_2_teachers()">���������</a>
                        <a href="#" class="easyui-linkbutton" style="width:170px;" iconCls="icon-del_list" onclick="clear_addr_teachers()">�������� ��������</a>                        
                      </div>
                   
                   
                   </div>
                   <!-- ����� �������������� DIV -������� ������� -->
                 
                 </div>
                 <!-- ����� ����������� layout ��� �������� ��� --> 
			  
              </div>
           
           </div>
           <!-- ����� ������ ����� ��� ����������� ������������ -->
    
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
    
    <!-- ����� ������ ��������� ��� �������� ��� -->    
    <div id="dlg_select_student" class="easyui-dialog" style="width:450px;height:500px;padding:10px 5px 0px 5px;"
            closed="true" modal="true" buttons="#dlg-buttons_stud" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <span id="lb_stud" style="float:left; font-weight: bold; margin-bottom:10px;">���-�� ��������� ���������:</span>
        <table id="dg_select_student" class="easyui-datagrid" style="width:100%;height:75%"
        method="get" fitColumns="true" sortName="FIO" sortOrder="asc" striped=true>

        <thead>
        <tr>
            <th field="ck_bx" checkbox="true"></th>
            <th field="Num_dogovor" width="40" sortable="true">�������</th>
            <th field="FIO" width="110" sortable="true">���</th>
            <th field="MOBILE_PHONE" width="60" sortable="true">���.�������</th>                                    
        </tr>
        </thead>
        </table>
        <!--������ ������� -->
            <div style="padding:10px 10px;">
            <a href="#" class="easyui-linkbutton" data-options="iconCls:'icon-filter'" onclick="\$('#dlg_filter_4_send_sms').window('open').dialog('center').dialog('setTitle','������')">������</a>
            </div>
        <!--����� ������ ������� -->
        <span id="lb_tie" style="float:right; color: #F00; font-weight: bold;"></span>
    </div> 
    <div id="dlg-buttons_stud">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="add_selected_students()" style="width:100px">��</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_select_student').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� ������ ��������� ��� �������� ��� -->
    
    <!-- ����� ��������� ������� ��� ������ �������� ��� �������� ��� -->    
    <div id="dlg_filter_4_send_sms" class="easyui-dialog" style="width:500px;height:220px;padding:10px 1px;"
            closed="true" modal="true" buttons="#dlg-buttons_4_send_sms" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">��������� �������</div>
        <form id="fm_filter_4_send_sms" novalidate>
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
    <div id="dlg-buttons_4_send_sms">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="doFilter_4_send_sms()" style="width:100px">����������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_filter_4_send_sms').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� ��������� ������� ��� ������ �������� ��� ������� ��� -->
	
	<!-- ����� ������ �������� ��� �������� ��� -->    
    <div id="dlg_select_teacher" class="easyui-dialog" style="width:450px;height:500px;padding:10px 5px 0px 5px;"
            closed="true" modal="true" buttons="#dlg-buttons_teachers" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <span id="lb_teachers" style="float:left; font-weight: bold; margin-bottom:10px;">���-�� ��������� ��������������:</span>
        <table id="dg_select_teachers" class="easyui-datagrid" style="width:100%;height:75%"
        method="get" fitColumns="true" sortName="FIO" sortOrder="asc" striped=true>

        <thead>
        <tr>
            <th field="ck_bx" checkbox="true"></th>
            <th field="FIO" width="110" sortable="true">���</th>
            <th field="PHONE" width="60" sortable="true">���.�������</th>                                    
        </tr>
        </thead>
        </table>      
    </div> 
    <div id="dlg-buttons_teachers">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="add_selected_teachers()" style="width:100px">��</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_select_teacher').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� ������ �������� ��� �������� ��� -->
    
    
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