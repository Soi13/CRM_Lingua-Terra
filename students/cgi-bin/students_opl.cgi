#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
#use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI::Session;
use CGI qw(:cgi);
use Digest::MD5 qw(md5_hex);
use ConnectDB;

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
        print "Location: https://students.linguaterra-soft.ru\n\n";
        exit();
        }

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:spending",User=>"root", Password=>""}) or die CGI::Session->errstr();
$sess->name('SID');

#���� ������ ������
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: https://students.linguaterra-soft.ru\n\n";
        exit();
        }

#���� ����� ������ �������
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: https://students.linguaterra-soft.ru\n\n";
        exit();
        }

#���� IP �� ���������
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: https://students.linguaterra-soft.ru\n\n";
        exit();
        }

#����������� ���������� ����� � ������ ������������ �� ������
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $num_dog=$sess->param('stud_num_dog');


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
        
        my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth=$dbh->do("SET NAMES 'cp1251'");
        my $sql="select FIO from pupils where Num_dogovor like ?";
        $sth=$dbh->prepare($sql);
        $sth->execute($num_dog);

        #� ������ ���������� ����������� ������
        my @row = $sth->fetchrow_array;

        $dbh->disconnect;

        my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time); 
        $mon=$mon+1;
        $year=$year+1900;
        
        print "Content-type: text/html\n\n";
        print <<HTML;
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset='windows-1251'>
		<meta name="viewport" content="width=device-width">
        <script src="https://3dsec.sberbank.ru/payment/docsite/assets/js/ipay.js"></script>
        <script>
          var ipay = new IPAY({api_token: 'YRF3C5RFICWISEWFR6GJ'});
        </script>
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>@pers_room</title>
        <link rel="stylesheet" type="text/css" href="../CSS/easyui.css">
        <link rel="stylesheet" type="text/css" href="../CSS/icon.css">
        <link rel="stylesheet" type="text/css" href="../CSS/demo.css">">
		<link rel="stylesheet" type="text/css" href="../CSS/color.css">">
        <link rel="stylesheet" href="../CSS/styles.css">
        <link rel="stylesheet" type="text/css" href="../CSS/font_roboto/roboto.css">        
        <script type="text/javascript" src="../JS/jquery.min.js"></script>
        <script type="text/javascript" src="../JS/jquery.easyui.min.js"></script>
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
                window.location.replace("https://students.linguaterra-soft.ru")}
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
       url:'get_pays_in_student.cgi?SID=$SID',
       columns:[[                                  
                 {field:'PERIOD',title:'������'},
                 {field:'SUMM_4_OPL',title:'����� ��� ������'},
                 {field:'OPL_SUMM',title:'���������� �����'},
                 {field:'DATE_OF_PAY',title:'���� �������'}                                                 
              ]]
       });       
       //////////////////////////////////////////
       
       //��������� ������������ ������ � ��������� �����            
       var ss = [];       
       \$.ajax({            
       type: 'GET',
       traditional: true,
       url: 'get_group_name.cgi?SID=$SID',
       //data: {'data':ss},            
       success: function(res) {
                                  \$('#group').text('������: '+res.result); //��������� ������������ � ��������� �����                                  
                                  \$('#p').show();
                                  \$('#p').progressbar({
                                                         value: res.proc
                                                      });
                                  \$('#paid').text('�������� ��������: '+res.summ_debt+' ���.'); 
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
       });
       </script>
	   
	  
	        
      
        
        </head>
        <body class="easyui-layout" onload="">
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
        <div data-options="region:'center',title:'������� ������� - �������/������. �������: $row[0]'">

        <!--������� �������� ������, ������ ��������� ����� � ������� ���������� �������-->
         <div style="margin-bottom: 10px; margin-top: 10px; margin-left: 5px;">
          <span id="group" style="font-weight: bold; float: left; margin-right: 10px;"></span>
          <div id="p" style="width:auto; height:15px; bold;"></div> 
          </br>
          <span id="paid" style="font-weight: bold;"></span>
          </br>          
          <div style="margin-top: 10px;"><span id="debt_4_today" style="font-weight: bold;"></span></div>
         </div>         
        <!--����� ������� �������� ������, ������ ��������� ����� � ������� ���������� �������-->
         
        <!-- ����� ������ ����� ��������-->
         <table id="list_of_pays" style="width:100%"></table>
        <!-- ����� ����� ������ ����� �������� -->
        
		
        <div style="margin-top:20px; margin-left:10%;"> 		
		  <a onclick="ipayCheckout({              
              currency:'RUB',
              description: '������-����� (������ �� ��������)'})"
              class="easyui-linkbutton c1" style="width:200px; height:40px;">��������
          </a>
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
    
    
        </body>
        </html>
HTML2

#���������� ����� ����� ������
$sess->atime(time());
$sess->flush();

#�������� ������
sub f_delete_session {
         #������� ����
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'https://students.linguaterra-soft.ru');
         print "Set-Cookie: $cookies\n";
         #������� ������
         $sess->delete();
         $sess->flush();
        }

#���������� SID � URL-������
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
else { print "Location: https://students.linguaterra-soft.ru\n\n"; }