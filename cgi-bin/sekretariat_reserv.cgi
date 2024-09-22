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
my $RESERV_SEKRETARIAT=$sess->param('RESERV_SEKRETARIAT');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

     if ($RESERV_SEKRETARIAT==1) #������� ����� �� ������ ������������ � ������ "������".
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
        <script type="text/javascript" src="../JS/jquery.min.js"></script>
        <script type="text/javascript" src="../JS/jquery.easyui.min.js"></script>
        <script type="text/javascript" src="../JS/dhtmlxscheduler.js"></script>
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
       //��������� � ��������� ����������� �� �������
       \$('#pg').propertygrid({
       method:'get',
       url: 'get_zayavki_reserv_detail.cgi?id_z='+row.ID+'&SID=$SID',
       showGroup: true,
       showHeader: false,
       scrollbarSize: 0
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
       
             
       <script>//��������� �������
       function doFilter(){
       
       //��������, ������ ���� �� ���� �������� ����������
       if((!\$("#radio_WHO_GET_ZAYAV").prop("checked")) && (!\$("#radio_SOURCE_ZAYAV").prop("checked")) && (!\$("#radio_DATE_OF_ZAYAV_FROM").prop("checked")) && (!\$("#radio_AGE_STUDENT").prop("checked")) && (!\$("#radio_BRANCH").prop("checked")) && (!\$("#radio_LANGUAGE").prop("checked")) && (!\$("#radio_LEVEL_KNOWLEDGE").prop("checked")) && (!\$("#radio_DATE_OF_TEST_FROM").prop("checked")) && (!\$("#radio_erase_filter").prop("checked")) && (!\$("#radio_DATE_OF_BORN_FROM").prop("checked"))) {
	    \$.messager.alert('��������','�� ������ �������� ����������!','warning');
	    return;
        }        
               
       ///////////////////
       if(\$("#radio_WHO_GET_ZAYAV").prop("checked")) { 
              \$('#dg').datagrid('load',{
             who_get_zayav: \$('#WHO_GET_ZAYAV').combobox('getValue')                                          
              });
              \$('#lb').text('���������� ������ �� "��� ������� ������"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_SOURCE_ZAYAV").prop("checked")) { 
              \$('#dg').datagrid('load',{
             source_zayav: \$('#SOURCE_ZAYAV').combobox('getValue')
              });
              \$('#lb').text('���������� ������ �� "�������� ������"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_DATE_OF_ZAYAV_FROM").prop("checked")) { 
              \$('#dg').datagrid('load',{
             date_of_zayav_from: \$('#DATE_OF_ZAYAV_FROM').datebox('getValue'),
             date_of_zayav_to: \$('#DATE_OF_ZAYAV_TO').datebox('getValue')             
              });
              \$('#lb').text('���������� ������ �� "���� ������"');
       }
       ///////////////////
              
       ///////////////////
       if(\$("#radio_AGE_STUDENT").prop("checked")) { 
              \$('#dg').datagrid('load',{
             age: \$('#AGE_STUDENT').val()
              });
              \$('#lb').text('���������� ������ �� "������� ��������"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_DATE_OF_BORN_FROM").prop("checked")) { 
              \$('#dg').datagrid('load',{
             date_of_born_from: \$('#DATE_OF_BORN_FROM').datebox('getValue'),
             date_of_born_to: \$('#DATE_OF_BORN_TO').datebox('getValue')             
              });
              \$('#lb').text('���������� ������ �� "���� ��������"');
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
              \$('#lb').text('���������� ������ �� "������� ��������"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_DATE_OF_TEST_FROM").prop("checked")) { 
              \$('#dg').datagrid('load',{
             date_of_test_from: \$('#DATE_OF_TEST_FROM').datebox('getValue'),
             date_of_test_to: \$('#DATE_OF_TEST_TO').datebox('getValue')             
              });
              \$('#lb').text('���������� ������ �� "���� �����"');
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
       
                      
       <script> //����������� ������ �� ������� Enter
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
        //���������� ���� TextBox ������� KeyUp ��� ������ �� ����
        \$('#fio').textbox({
	                      inputEvents:\$.extend({},\$.fn.textbox.defaults.inputEvents,{
		              keyup:function(e){
			                          doSearch();
		                               }
	                      })
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
        
         <table id="pg" style="width:100%"></table>
        
        </div>
        <!-- ����� ������ DIV ������ ����������� -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->

        <!-- ����������� DIV -������� ������� -->
        <div data-options="region:'center',title:'������� ������� - ������. ������������: $formLogin'">

        <table id="dg" title="������" class="easyui-datagrid" style="width:100%;height:100%"
        method="get"
        url="get_zayavki_reserv.cgi?SID=$SID"
        toolbar="#tb, #toolbar"
        rownumbers="true" fitColumns="true" singleSelect="true" pagination="true" sortName="FIO_STUDENT" sortOrder="asc">

        <thead>
        <tr>
            <th field="ID" width="15" sortable="true" hidden="true">ID1</th>
            <th field="DATE_GET_ZAYAV" width="20" sortable="true">���� ������</th>
            <th field="FIO_STUDENT" width="60" sortable="true">��� ��������</th>
            <th field="LANG" width="60" sortable="true">����</th>
            <th field="LEVEL" width="25" sortable="true">������� ��������</th>            
            <th field="AGE_STUDENT" width="25">������� ��������</th>
            <th field="BR" width="27">������</th>
        </tr>
        </thead>
        </table>
        <div id="toolbar">
        <a href="#" class="easyui-linkbutton" iconCls="icon-filter" plain="true" onclick="\$('#dlg_filter').window('open').dialog('center').dialog('setTitle','������')">������</a>
        <span id="lb" style="float:right; color: #F00; font-weight: bold;"></span>
        </div>

        <!-- ������ ������ -->
        <div id="tb" style="padding:3px">
             <span>����� �� ��� ��������:</span>
             <input id="fio" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
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
    
     
    <!-- ����� ��������� ������� ������ -->    
    <div id="dlg_filter" class="easyui-dialog" style="width:530px;height:400px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">��������� �������</div>
        <form id="fm_filter" novalidate>
            <table>
                <tr>
                    <td><label><input id="radio_WHO_GET_ZAYAV" name="radio" type="radio" value="0" />������ ������:</label></td>
                    <td><input id="WHO_GET_ZAYAV" name="WHO_GET_ZAYAV" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'users_get_zayav.cgi?SID=$SID', method: 'get'"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_SOURCE_ZAYAV" name="radio" type="radio" value="1" />�������� ������:</label></td>
                    <td><input id="SOURCE_ZAYAV" name="SOURCE_ZAYAV" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', valueText: 'text', url: 'users_get_source_zayav.cgi?SID=$SID', method: 'get'"></input></td>
                </tr>
                <tr>
                    <td><label><input id="radio_DATE_OF_ZAYAV_FROM" name="radio" type="radio" value="2" />���� ������:    ��--</label></td>
                    <td><input id="DATE_OF_ZAYAV_FROM" name="DATE_OF_ZAYAV_FROM" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser">   ��--<input id="DATE_OF_ZAYAV_TO" name="DATE_OF_ZAYAV_TO" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_AGE_STUDENT" name="radio" type="radio" value="3" />������� ��������:</label></td>
                    <td><input id="AGE_STUDENT" name="AGE_STUDENT" class="easyui-textbox"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_DATE_OF_BORN_FROM" name="radio" type="radio" value="9" />���� ����.:    ��--</label></td>
                    <td><input id="DATE_OF_BORN_FROM" name="DATE_OF_BORN_FROM" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser">   ��--<input id="DATE_OF_BORN_TO" name="DATE_OF_BORN_TO" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_BRANCH" name="radio" type="radio" value="4" />������:</label></td>
                    <td><input id="BRANCH" name="BRANCH" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', valueText: 'text', url: 'get_branches.cgi?SID=$SID', method: 'get'"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_LANGUAGE" name="radio" type="radio" value="5" />����:</label></td>
                    <td><input id="LANGUAGE" name="LANGUAGE" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', valueText: 'text', url: 'get_languages.cgi?SID=$SID', method: 'get'"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_LEVEL_KNOWLEDGE" name="radio" type="radio" value="6" />������� ��������:</label></td>
                    <td><input id="LEVEL_KNOWLEDGE" name="LEVEL_KNOWLEDGE" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', valueText: 'text', url: 'get_level_knowledge.cgi?SID=$SID', method: 'get'"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_DATE_OF_TEST_FROM" name="radio" type="radio" value="7" />���� ������������:  ��--</label></td>
                    <td><input id="DATE_OF_TEST_FROM" name="DATE_OF_TEST_FROM" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser">   ��--<input id="DATE_OF_TEST_TO" name="DATE_OF_TEST_TO" class="easyui-datebox" data-options="formatter:myformatter, parser:myparser"></td>
                </tr>                
                <tr>
                    <td><label><input id="radio_erase_filter" name="radio" type="radio" value="8" /><strong>����� �������:</strong></label></td>                    
                </tr>
            </table>    
        </form>
    </div>
    <div id="dlg-buttons">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="doFilter()" style="width:100px">����������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg_filter').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� ��������� ������� ������ -->
    
    
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