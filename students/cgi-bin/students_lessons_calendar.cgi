#!/usr/bin/perl -w
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

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:a0018982_fin",User=>"a0018982_oleg", Password=>""}) or die CGI::Session->errstr();
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
        print "Location: http://students.linguaterra-soft.ru\n\n";
        exit();
        }

#���� IP �� ���������
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: http://students.linguaterra-soft.ru\n\n";
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
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>@pers_room</title>
        <link rel="stylesheet" type="text/css" href="../CSS/easyui.css">
        <link rel="stylesheet" type="text/css" href="../CSS/icon.css">
        <link rel="stylesheet" type="text/css" href="../CSS/demo.css">">
        <link rel="stylesheet" type="text/css" href="../CSS/dhtmlxscheduler.css">        
        <link rel="stylesheet" href="../CSS/styles.css">
        <link rel="stylesheet" href="../CSS/multiline_scheduler.css">
        <link rel="stylesheet" type="text/css" href="../CSS/dhtmlxchart.css">
        <link rel="stylesheet" type="text/css" href="../CSS/font_roboto/roboto.css"> 
        <script type="text/javascript" src="../JS/jquery.min.js"></script>
        <script type="text/javascript" src="../JS/jquery.easyui.min.js"></script>
        <script type="text/javascript" src="../JS/dhtmlxscheduler.js"></script>
        <script type="text/javascript" src="../JS/dhtmlxscheduler_year_view.js"></script>
        <script type="text/javascript" src="../JS/locale_ru.js" charset="utf-8"></script>
        <script type="text/javascript" src="../JS/dhtmlxscheduler_active_links.js"></script>               
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
        //��������� � ��������� ���� �� ��������
        \$('#pers_info').propertygrid({
        method:'get',
        url: 'get_student_detail.cgi?SID=$SID',
        showGroup: true,
        showHeader: false,
        scrollbarSize: 0,
        nowrap: false
        });
       //////////////////////////////////////////       
        
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
		scheduler.load("get_calendar_events.cgi?SID=$SID","json");
		
		scheduler.templates.event_bar_date = function(start,end,ev){
                return "� <b>"+scheduler.templates.event_date(start)+" - "+scheduler.templates.event_date(end)+"</b> ";
                };
		
	}
        </script>
       
      
        
        </head>
        <body class="easyui-layout" onload="init();">
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
        <div data-options="region:'center',title:'������� ������� - ������ ��������. �������: $row[0]'">

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
                  <div class="dhx_cal_tab" name="year_tab" style="right:268px;"></div>                
               </div>
               <div class="dhx_cal_header"></div>
               <div class="dhx_cal_data"></div>
           </div>        
           <!-- ����� ��������� -->
                  

       

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