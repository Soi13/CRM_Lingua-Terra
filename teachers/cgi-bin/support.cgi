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

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {
        #���������� �������� ����������� ��� ������ �� �� ��������
        open FF, "<txt_data/pers_room.txt";
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
        <link rel="stylesheet" href="../CSS/styles.css">
        <link rel="stylesheet" href="../CSS/multiline_scheduler.css">  
        <script type="text/javascript" src="../JS/jquery.min.js"></script>
        <script type="text/javascript" src="../JS/jquery.easyui.min.js"></script>
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
       
       <script> //����������� ���������� ckeditor ������ TEXAREA
       \$(function(){                 
       \$('#TEXT_OF_DOCUMENT').ckeditor({uiColor:'#FDE0B0', fullPage:true});  
                 })
       </script>
       
       <script>
       function send_message() {
        var msg   = \$('#fm_message').serialize();
        \$.ajax({
          type: 'GET',
          url: 'send_message.cgi?SID=$SID',
          data: msg,
          success: function(res) { \$.messager.alert('����������',res.result,'info'); if (res.result=="��������� ���������� �������!") {\$('#fm_message').form('clear');}},
          error: function() {alert("did not work");}
        });        
       }
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
        
        print <<HTML_e;
        </div>
        <!--����� ����� DIV ������ ���� -->

        <!-- ������ DIV ������ ����������� -->
        <!-- <div data-options="region:'east',split:true,title:'�����������'" style="width:30%;padding:1px;"> -->
        <!-- </div> -->
        <!-- ����� ������ DIV ������ ����������� -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->

        <!-- ����������� DIV -������� ������� -->
        <div data-options="region:'center',title:'������� ������� - ����������� ���������. ������������: $formLogin'">

         <form id="fm_message" novalidate> 
         <div style="margin-left:10px; margin-top:20px;">
           <label><b>���� ���������:</b></label>
           <br />
           <input name="TOPIC_MESSAGE" class="easyui-textbox" style="width:100%">
           <br />
         </div>
         <div style="margin-left:10px; margin-top:50px;">      
           <label><b>����� ���������:</b></label>
           <br />
           <textarea name="TEXT_OF_DOCUMENT" id="TEXT_OF_DOCUMENT" rows="20" cols="80"></textarea>               
         </div>        
         <div style="margin-left:45%; margin-top:10px;;">
           <a href="javascript:void(0)" class="easyui-linkbutton" iconCls="icon-ok" onclick="send_message()" style="width:200px">���������</a>
         </div>
        </div>
        </form>
              
    

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
           
        </body>
        </html>
HTML_e

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