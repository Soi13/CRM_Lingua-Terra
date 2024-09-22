#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
#use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI::Session;
use CGI qw(:cgi);
use Digest::MD5 qw(md5_hex);

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

#���� ������ ������
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

#���� ����� ������ �������
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

#���� IP �� ���������
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: http://teachers.localhost:6080\n\n";
        exit();
        }

#����������� ���������� ����� � ������ ������������ �� ������
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $days_expired=$sess->param('days_expired_passw');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {
        #���������� �������� ������ ������� ��� ������ �� �� ��������
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

        my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time); 
        $mon=$mon+1;
        $year=$year+1900;
        
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
        <link rel="stylesheet" type="text/css" href="../CSS/dhtmlxscheduler.css">        
        <link rel="stylesheet" href="../CSS/styles.css">
        <link rel="stylesheet" type="text/css" href="../CSS/dhtmlxchart.css">
        <link rel="stylesheet" type="text/css" href="../CSS/font_roboto/roboto.css"> 
        <script type="text/javascript" src="../JS/jquery.min.js"></script>
        <script type="text/javascript" src="../JS/jquery.easyui.min.js"></script>
        <script type="text/javascript" src="../JS/dhtmlxscheduler.js"></script>
        <script src="../JS/script.js"></script>
        <script src="../JS/dhtmlxchart.js"></script>
 

        <script>
        function confirm1(){
        \$.messager.confirm('��������', '�� �������, ��� ���������� �����', function(r){
        if (r){
        //alert('confirmed: '+r);
        window.location.replace("/cgi-bin/exit.cgi?SID=$SID");
        }     });  }   </script>

        <!--Increase time of life session-->
        <script>
        \$(document).mouseup(function (e){
        \$.ajax({
                url: '/cgi-bin/session_alive.cgi?SID=$SID',
                success: function(){
                window.location.replace("http://teachers.localhost:6080")}
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
	\$(function(){
	\$('#panel_birthday').panel({
                                      width:352,
                                      height:252,
                                      href:'get_birthdays.cgi?SID=$SID'  
    
                                   }); 
	            });
	</script>
	
	
        <script>
        \$(function(){  
           var days=$days_expired;
           
           switch (days){
             case 1:
             \$.messager.alert('����������', '���� �������� ������ �������� ����� 1 ����. ������������� �������� ���, ����� ������� ������ ����� �������������!', 'info');
             break;
             case 2:
             \$.messager.alert('����������', '���� �������� ������ �������� ����� 2 ���. ������������� �������� ���, ����� ������� ������ ����� �������������!', 'info');
             break;
             case 3:
             \$.messager.alert('����������', '���� �������� ������ �������� ����� 3 ���. ������������� �������� ���, ����� ������� ������ ����� �������������!', 'info');
             break;
             case 4:
             \$.messager.alert('����������', '���� �������� ������ �������� ����� 4 ���. ������������� �������� ���, ����� ������� ������ ����� �������������!', 'info');
             break;
             case 5:
             \$.messager.alert('����������', '���� �������� ������ �������� ����� 5 ����. ������������� �������� ���, ����� ������� ������ ����� �������������!', 'info');
             break;               
           }      
        })
        </script>
		
		<script> //��������� �������� ��� ��� ������������
        \$(function(){	
         \$.ajax({
            type: 'GET',
            url: 'get_agenda.cgi?SID=$SID',
            cache: false,
            success: function(res1) {   
                                       if (res1.rows.length>0)
                                       {
                                        //alert(res1.rows[0].START_DATE);
                                        \$('#dlg_open_agenda').window('open').dialog('center').dialog('setTitle','�������� ��� �� ������� ���������');
                                        \$('#dg_agenda').datagrid({data: res1});                                     
                                       }
                                     },
            error: function() {alert("did not work");}
            });
                
        })
        </script>
        
       <script>//������� ��������� ������ �������
       \$(function(){       
       \$('#dg_agenda').datagrid({
	rowStyler: function(index,row){
		if (row.KIND_EVENT=="calls"){ return 'background-color:blue;color:#fff;'; }
		if (row.KIND_EVENT=="linguaterria"){ return 'background-color:#FC5BD5;color:#fff;'; }
		if (row.KIND_EVENT=="dogovor"){ return 'background-color:red;color:#fff;'; }
		if (row.KIND_EVENT=="test"){ return 'background-color:orange;color:#fff;'; }
		if (row.KIND_EVENT=="event"){ return 'background-color:#36BD14;color:#fff;'; }
		if (row.KIND_EVENT==""){ return 'background-color:#1796b0;color:#fff;'; }
	        }
        });         
        })
        </script> 
        
        </head>
        <body class="easyui-layout">
        <!--������� DIV - ��������� -->
        <div data-options="region:'north',border:false" style="height:100px;background:#f0993c;padding:10px;"><h1 class="shd">@pers_room</h1>
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
HTML1
		#���������� ����
        open FF2, "<txt_data/main_menu.txt";
        my @menu_panel=<FF2>;
        foreach my $str_menu (@menu_panel)
        {
           $str_menu=~s/\0//g;
           $str_menu=~s/\.\.//g;
           $str_menu=~s/[<]*script[^>]*>.*[<]*\/script[>]*//i; #�� ���� ������ ������� ���� <script>
           $str_menu=~s/SID=\$SID/SID=$SID/i; #����������� ���������� ���� SID � ������ ������ ���������� $SID. ��� �� �� �������������, �.�. ������ �������� �� ���������� �����.
        }
        close (FF2) or die $!;        
        print @menu_panel;
        #########################################             

        print <<HTML2;
        </div>
        <!--����� ����� DIV ������ ���� -->

        <!-- ������ DIV ������ ����������� -->
        <!--<div data-options="region:'east',split:true,title:'�����������'" style="width:30%;padding:1px;">-->
        <!--</div>-->
        <!-- ����� ������ DIV ������ ����������� -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->

        <!-- ����������� DIV -������� ������� -->
        <div data-options="region:'center',title:'������� ������� - �������. ������������: $formLogin'">

        <!-- ��������� -->
        <div style="float:left">
           <div id="panel_birthday" style="border-color:#999; padding-top:10px;"><header style="background-color: #FFFFFF; border-color:#999; color:red;">������� ���� �������� �:</header></div>
        </div>
        
        <div>
          <div id="chartdiv" style="width:650px; height:250px; font-size:11px;"></div>
        </div>
        <!-- ����� ��������� -->

        <div style="margin-top: 25px; margin-left:20px;">
            <a href="https://us02web.zoom.us/j/9510088475?pwd=MmNyb0djck9Kb3cwaTRoL0p0WFFxdz09"><span style="font-size:18px;">������������ � �����</span></a>
        </div>

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
	
	<!-- ����� ������ �������� ��� -->    
    <div id="dlg_open_agenda" class="easyui-dialog" style="width:80%;height:500px;padding:10px 5px 0px 5px;"
            closed="true" modal="true" buttons="#dlg_buttons_agenda" data-options="openDuration:400, closeDuration:400, closeAnimation:'fade', openAnimation:'fade'">             
        <h1 class="shad">�������� ���</h1>                   
        <table id="dg_agenda" class="easyui-datagrid" style="width:100%;height:75%"
        method="get" rownumbers="true" singleSelect="true" fitColumns="true" sortOrder="asc" striped=true>
        <thead>
        <tr>
            <th field="ID" width="10" hidden="true">ID</th>
            <th field="START_DATE" width="30">���� � ����� ������ �������</th>
            <th field="TEXT_MESSAGE" width="70">�������</th>
            <th field="DETAILS" width="60">�����������</th>                                    
            <th field="KIND_EVENT" width="10" hidden="true">ID</th>
        </tr>
        </thead>
        </table>                
    </div> 
    <div id="dlg_buttons_agenda">
        <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="javascript:\$('#dlg_open_agenda').dialog('close')" style="width:90px">�������</a>
    </div>
    <!-- ����� ����� ������ �������� ��� -->
    
        </body>
        </html>
HTML2

#���������� ����� ����� ������
$sess->atime(time());
$sess->flush();

#�������� ������
sub f_delete_session {
         #������� ����
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://teachers.localhost:6080');
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
else { print "Location: http://teachers.localhost:6080\n\n"; }