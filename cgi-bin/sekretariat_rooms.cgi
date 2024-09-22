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
my $ROOMS_SEKRETARIAT=$sess->param('ROOMS_SEKRETARIAT');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

    if ($ROOMS_SEKRETARIAT==1) #������� ����� �� ������ ������������ � ������ "��������".
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
       //room: \$('#room').val()
	   room: \$('#room').textbox('getText')
       });
       }
       </script>

       <script>
       \$(function(){
       \$('#dg').datagrid({
       onSelect:function(index){
       var row = \$('#dg').datagrid('getSelected');       
       //��������� � ��������� ����������� �� ���������
       \$('#pg').propertygrid({
       method:'get',
       url: 'get_rooms_detail.cgi?id_z='+row.ID+'&SID=$SID',
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
        var url;
        function newRoom(){
            \$('#dlg').dialog('open').dialog('center').dialog('setTitle','����� �������');
            \$('#fm').form('clear');
            url = 'insert_room.cgi?SID=$SID';
        }
        function editRoom(){
            var row = \$('#dg').datagrid('getSelected');
            if (row){
	    \$('#dlg').dialog('open').dialog('center').dialog('setTitle','�������������� ��������');
            \$('#fm').form('load',row);               
            url = 'edit_room.cgi?id_x='+row.ID+'&SID=$SID';                                          
            }
        }
        
        function saveRoom() {
        var msg   = \$('#fm').serialize();
        \$.ajax({
          type: 'GET',
          url: url,
          data: msg,
          success: function(res) { \$.messager.alert('����������',res.result,'info'); if (res.result=="������� �������� �������!") {\$('#fm').form('clear'); \$('#dlg').dialog('close'); \$('#dg').datagrid('reload');} if (res.result=="������� �������������� �������!") {\$('#fm').form('clear'); \$('#dlg').dialog('close'); \$('#dg').datagrid('reload');}},
          error: function() {alert("did not work");}
        });        
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
		//scheduler.config.readonly = true;
		scheduler.config.readonly_form = true;
				
		scheduler.config.lightbox.sections = [
				{name:"�������� �������", height:130, map_to:"text", type:"textarea" , focus:true},
				{name:"�����������", height:43, type:"textarea", map_to:"details" },
				{name:"time", height:72, type:"time", map_to:"auto"}
			];
	
		scheduler.init('scheduler_here',new Date(),"month");
		scheduler.setLoadMode("month");		
		scheduler.load("get_calendar_events_students.cgi?SID=$SID","json");	
        	
		
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
       if((!\$("#radio_ROOM_NAME").prop("checked")) && (!\$("#radio_CAPACITY_ROOM").prop("checked")) && (!\$("#radio_BRANCH").prop("checked")) && (!\$("#radio_erase_filter").prop("checked"))) {
	    \$.messager.alert('��������','�� ������ �������� ����������!','warning');
	    return;
        }        
               
       ///////////////////
       if(\$("#radio_ROOM_NAME").prop("checked")) { 
              \$('#dg').datagrid('load',{
             room_name: \$('#ROOM_NAME').combobox('getValue')                                          
              });
              \$('#lb').text('���������� ������ �� "�����/������������ ��������"');
       }
       ///////////////////
       
       ///////////////////
       if(\$("#radio_CAPACITY_ROOM").prop("checked")) { 
              \$('#dg').datagrid('load',{
             capacity_room: \$('#CAPACITY_ROOM').combobox('getValue')
              });
              \$('#lb').text('���������� ������ �� "����������� ��������"');
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
	    var t = \$('#room');
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
        \$('#room').textbox({
	                      inputEvents:\$.extend({},\$.fn.textbox.defaults.inputEvents,{
		              keyup:function(e){
			                          doSearch();
		                               }
	                      })
                           })
        
        })
        </script>
       
               
    
        </head>
 
 
        <body class="easyui-layout" onload="init()";>
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
         <div title="��������� ����">
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
                  <div class="dhx_cal_tab" name="year_tab" style="right:268px; width:20px"></div>
               </div>
               <div class="dhx_cal_header"></div>
               <div class="dhx_cal_data"></div>
           </div>        
           <!-- ����� ��������� -->
         
         </div>
         
         </div>
        <!-- ����� ������ TABS -->
         
         
        
        </div>
        <!-- ����� ������ DIV ������ ����������� -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->

        <!-- ����������� DIV -������� ������� -->
        <div data-options="region:'center',title:'������� ������� - ��������. ������������: $formLogin'">

        <table id="dg" title="��������" class="easyui-datagrid" style="width:100%;height:100%"
        method="get"
        url="get_rooms.cgi?SID=$SID"
        toolbar="#tb, #toolbar"
        rownumbers="true" fitColumns="true" singleSelect="true" pagination="true" sortName="ROOM_NAME" sortOrder="asc">

        <thead>
        <tr>
            <th field="ID" width="15" sortable="true" hidden="true">ID1</th>
            <th field="ROOM_NAME" width="200" sortable="true">������������ ��������</th>
            <th field="CAPACITY_ROOM" width="60" sortable="true">����������� ��������</th>
            <th field="ADDRESS_ROOM" width="60" sortable="true">����� ��������</th>            
        </tr>
        </thead>
        </table>
        <div id="toolbar">
        <a href="#" class="easyui-linkbutton" iconCls="icon-add" plain="true" onclick="newRoom()">�������� �������</a>
        <a href="#" class="easyui-linkbutton" iconCls="icon-edit" plain="true" onclick="editRoom()">������������� �������</a>
        <a href="#" class="easyui-linkbutton" iconCls="icon-filter" plain="true" onclick="\$('#dlg_filter').window('open').dialog('center').dialog('setTitle','������')">������</a>
        <span id="lb" style="float:right; color: #F00; font-weight: bold;"></span>
        </div>

        <!-- ������ ������ -->
        <div id="tb" style="padding:3px">
             <span>����� �� ������������ ��������:</span>
             <input id="room" class="easyui-textbox" data-options="iconCls:'icon-search'" style="line-height:20px;border:1px solid #ccc; border-radius:3px; width:200px;">
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
    
    <!-- ����� ���������� ������ �������� -->    
    <div id="dlg" class="easyui-dialog" style="width:500px;height:430px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">���������� � ��������</div>
        <form id="fm" novalidate>
            <div class="fitem">
               	<label>�����/������������ ��������:</label>
               	<input name="ROOM_NAME" class="easyui-textbox" required missingMessage="������ ���� ���������� ���������">
           	</div>
            <div class="fitem">
               	<label>����������� ��������:</label>
               	<input name="CAPACITY_ROOM" class="easyui-textbox">
           	</div>
            <div class="fitem">
               	<label>����� ��������:</label>
               	<input name="ADDRESS_ROOM" class="easyui-textbox">
	        </div>
            <div class="fitem">
               	<label>������:</label>
               	<input name="BRANCH" class="easyui-combobox" data-options="editable:false, required:true, panelHeight:'auto', valueField: 'id', textField: 'text', url: 'get_branches.cgi?SID=$SID', method: 'get'" missingMessage="������ ���� ���������� ���������">
	        </div>
            <div class="fitem">
               	<label>��������:</label>
               	<input name="DESCRIPTION" class="easyui-textbox" data-options="multiline:true" style="height:100px">
	        </div>
            <div class="fitem">
               	<label>������� ��� �����:</label>
               	<input name="LESSONS_OUT_OF_SCHOOL" class="easyui-switchbutton" value="1" data-options="onText:'��',offText:'���'">
	        </div>        
        </form>
    </div>
    <div id="dlg-buttons">
        <a href="javascript:void(0)" class="easyui-linkbutton c6" iconCls="icon-ok" onclick="saveRoom()" style="width:100px">���������</a>
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-cancel" onclick="javascript:\$('#dlg').dialog('close')" style="width:90px">��������</a>
    </div>
    <!-- ����� ����� ���������� ����� ������ -->
    
    
    <!-- ����� ��������� ������� ������ -->    
    <div id="dlg_filter" class="easyui-dialog" style="width:530px;height:400px;padding:10px 1px;"
            closed="true" buttons="#dlg-buttons" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">
        <div class="ftitle">��������� �������</div>
        <form id="fm_filter" novalidate>
            <table>
                <tr>
                    <td><label><input id="radio_ROOM_NAME" name="radio" type="radio" value="0" />�����/������������ ��������:</label></td>
                    <td><input id="ROOM_NAME" name="ROOM_NAME" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'text', url: 'get_rooms_4_filter.cgi?SID=$SID', method: 'get'"></td>
                </tr>
                <tr>
                    <td><label><input id="radio_CAPACITY_ROOM" name="radio" type="radio" value="1" />����������� ��������:</label></td>
                    <td><input id="CAPACITY_ROOM" name="CAPACITY_ROOM" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'text', url: 'get_capacity_4_filter.cgi?SID=$SID', method: 'get'"></input></td>
                </tr>
                <tr>
                    <td><label><input id="radio_BRANCH" name="radio" type="radio" value="4" />������:</label></td>
                    <td><input id="BRANCH" name="BRANCH" class="easyui-combobox" data-options="editable:false, panelHeight:'auto', valueField: 'id', valueText: 'text', url: 'get_branches.cgi?SID=$SID', method: 'get'"></td>
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