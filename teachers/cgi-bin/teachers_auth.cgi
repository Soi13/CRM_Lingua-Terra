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

my $err="";
my $login=param('firstname');
my $passw=param('passw');

$login=~s/\0//g; $login=~s/\.\.//g; $login=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$passw=~s/\0//g; $passw=~s/\.\.//g; $passw=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;


if (defined($login) && defined($passw))
{
$passw=md5_hex($passw);

#�������� �� ������������� ������� � �� �� ���������� ������ � ������
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");
my $sql="select ID, FIO, BLOCKED, LOGIN, PASSW, PASSW_DAYS_OF_LIVE, PASSW_DATE_EXPIRED, ACTIVE_ONLINE_ROOM from teachers where LOGIN like ? and PASSW like ?";
$sth=$dbh->prepare($sql);
$sth->execute($login,$passw);

#�������� ���-�� �����, ���� ������ ����, �� ����� � ������ ������� �����
my $rows_affected = $sth->rows();

#� ������ ���������� ����������� ������
my @row = $sth->fetchrow_array;

$dbh->disconnect;


#���� ������ � ����� ������, �� ��������� ������ ������������ � ������� ������� �����
if ($row[3] eq $login && $row[4] eq $passw) {
#if ($rows_affected==1) {


if ($row[7]!=1) #�������� ����� �� ���������� ������
{
   print "Content-type: text/html\n\n";
   print <<HTML4;
   <!doctype html>
   <html>
   <head>
   <meta charset="windows-1251">
   <META NAME="ROBOTS" CONTENT="NOINDEX,NOFOLLOW" />
   <title>������ ������� ������������� ������-�����</title>
   <link href="../CSS/teachers_auth_page.css" rel="stylesheet">
   <script type="text/javascript" src="../JS/auth_check.js"></script>
   <script type="text/javascript" src="../JS/jquery.min.js"></script>
   </head>
   <body>
   <div class="header_teacher">������ ������� �������������</div>
   <form method="post" class="form-container" action="teachers_auth.cgi" onSubmit="return check()" name="forma" id="forma">
   <div class="form-title"><h2>�����������</h2></div>
   <div class="form-title">�����</div>
   <input class="form-field" type="text" name="firstname" id="firstname" autocomplete="off" /><br />
   <div class="form-title">������</div>
   <input class="form-field" type="password" name="passw" id="passw" autocomplete="off" /><br />
   <div class="submit-container">
   <input name="btn" id="btn" class="submit-button" type="submit" value="�����" />
   </div>
   </form>
   <p></p>
   <span class="err">������������ $row[3] ������������!</span>
   </body>
   </html>
HTML4
exit;
}
else
{   
   #������ ���-�� ���� ���������� �� ����������� ������� ������������� ����� ������
   my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
   my $sth2=$dbh2->do("SET NAMES 'cp1251'");
   my $sql2="SELECT DATEDIFF(PASSW_DATE_EXPIRED, NOW()) as DAYS from teachers where ID=?";
   $sth2=$dbh2->prepare($sql2);
   $sth2->execute($row[0]);
   #� ������ ���������� ����������� ������
   my @days = $sth2->fetchrow_array;
   $dbh2->disconnect;
   
   if ($days[0]==0) #���� ���-�� ���� �� ��������� ������ 0, �� ��������� ������
   {
      my $dbh3=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
      my $sth3=$dbh3->do("SET NAMES 'cp1251'");
      my $sql3="update teachers set ACTIVE_ONLINE_ROOM=0 where ID=?";
      $sth3=$dbh3->prepare($sql3); #��� �������� ������� �� ���������� ��������
      $sth3->execute($row[0]);
      $dbh3->disconnect;
      
      print "Content-type: text/html\n\n";
      print <<HTML4;
      <!doctype html>
      <html>
      <head>
      <meta charset="windows-1251">
      <META NAME="ROBOTS" CONTENT="NOINDEX,NOFOLLOW" />
      <title>������ ������� ������������� ������-�����</title>
      <link href="../CSS/blocked_page.css" rel="stylesheet">
      <link rel="stylesheet" type="text/css" href="../CSS/easyui.css">
      <link rel="stylesheet" type="text/css" href="../CSS/icon.css">
      <link rel="stylesheet" type="text/css" href="../CSS/demo.css">
      <script type="text/javascript" src="../JS/auth_check.js"></script>
      <script type="text/javascript" src="../JS/jquery.min.js"></script>    
      <script type="text/javascript" src="../JS/jquery.easyui.min.js"></script> 
      </head>
      <body>
      <form method="post" class="form-container" action="" onSubmit="" name="forma" id="forma">
      <p>���� ������� ������ ������������� � ����� � ���������� ����� �������� ������. ��� ������������� � ������������� ������� ���������� � ��������������.</p>
      <div class="submit-container">
      <a href="#" class="easyui-linkbutton" onclick="javascript: window.location.replace('http://teachers.localhost:6080');">�������</a>
      </div>
      </form>     
      </body>
      </html>      
HTML4

      exit();
   }
 
    
   #��� ������ ���������� ������ ��������������� ������� � �� ��� ����������
   #my $dbh1=DBI->connect("DBI:mysql:spending", "root", "89302810") or die "Error: $DBI::errstr\n";
   my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
   my $sth1=$dbh1->do("SET NAMES 'cp1251'");
   my $sql1="insert into logged_teachers (TEACHER_NAME, REMOTE_ADDR, REMOTE_PORT, REMOTE_HOST, USER_AGENT, DT_TM) values (?,?,?,?,?,NOW())";
   $sth1=$dbh1->prepare($sql1); #��� �������� ������� �� ���������� ��������
   $sth1->execute($login, $ENV{'REMOTE_ADDR'}, $ENV{'REMOTE_PORT'}, $ENV{'REMOTE_HOST'}, $ENV{'HTTP_USER_AGENT'});
   $dbh1->disconnect;

   #���������� �������� ����������� ��� ������ �� �� ��������
    open FF, "<txt_data/pers_room.txt";
    my @pers_room=<FF>;
    close (FF) or die $!;
   #########################################

   my $sess=CGI::Session->new("driver:mysql", undef, {DataSource=>"dbi:mysql:spending",User=>"root", Password=>""}) or die  CGI::Session->errstr();
   $sess->name('SID');
   my $cookies=cookie(-name=>$sess->name(), -valur=>$sess->id(), -path=>'/', -domain=>'http://teachers.localhost');
   print "Set-Cookie: $cookies\n";
   $sess->param(-name=>'Login', -value=>$login);
   $sess->param(-name=>'Password', -value=>$passw);
   $sess->param(-name=>'days_expired_passw', -value=>$days[0]);
   $sess->param(-name=>'teacher_id', -value=>$row[0]);
   $sess->expire("+30m");
   $sess->flush();
   print "Location: teachers_main.cgi?SID=" . $sess->id() . "\n\n";
   exit();
}
}
#�����, ���� ������ � ����� �� ������
else {
   print "Content-type: text/html\n\n";
   print <<HTML2;
   <!doctype html>
   <html>
   <head>
   <meta charset="windows-1251">
   <META NAME="ROBOTS" CONTENT="NOINDEX,NOFOLLOW" />
   <title>������ ������� ������������� ������-�����</title>
   <link href="../CSS/teachers_auth_page.css" rel="stylesheet">
   <script type="text/javascript" src="../JS/auth_check.js"></script>
   <script type="text/javascript" src="../JS/jquery.min.js"></script>
   </head>
   <body>
   <div class="header_teacher">������ ������� �������������</div>
   <form method="post" class="form-container" action="teachers_auth.cgi" onSubmit="return check()" name="forma" id="forma">
   <div class="form-title"><h2>�����������</h2></div>
   <div class="form-title">�����</div>
   <input class="form-field" type="text" name="firstname" id="firstname" autocomplete="off" /><br />
   <div class="form-title">������</div>
   <input class="form-field" type="password" name="passw" id="passw" autocomplete="off" /><br />
   <div class="submit-container">
   <input name="btn" id="btn" class="submit-button" type="submit" value="�����" />
   </div>
   </form>
   <p></p>
   <span class="err">����� ��� ������ �� ������!</span>
   </body>
   </html>
HTML2
  }
exit();
}

####################################################################################################################################
#�������� ����� ��������������. ���������� ��� ������ �����, ����� ���������� ������ � ������ ��� �� �����������, �.�. �� ���������#
####################################################################################################################################
print "Content-type: text/html\n\n";
print <<HTML3;
<!doctype html>
<html>
<head>
<meta charset="windows-1251">
<META NAME="ROBOTS" CONTENT="NOINDEX,NOFOLLOW" />
<title>������ ������� ������������� - ������-�����</title>
<link href="../CSS/teachers_auth_page.css" rel="stylesheet">
<script type="text/javascript" src="../JS/auth_check.js"></script>
<script type="text/javascript" src="../JS/jquery.min.js"></script>
</head>
<body>
<div class="header_teacher">������ ������� �������������</div>
<form method="post" class="form-container" action="/cgi-bin/teachers_auth.cgi" onSubmit="return check()" name="forma" id="forma">
<div class="form-title"><h2>�����������</h2></div>
<div class="form-title">�����</div>
<input class="form-field" type="text" name="firstname" id="firstname" autocomplete="off" /><br />
<div class="form-title">������</div>
<input class="form-field" type="password" name="passw" id="passw" autocomplete="off" /><br />
<div class="submit-container">
<input name="btn" id="btn" class="submit-button" type="submit" value="�����" />
</div>
</form>
<p></p>
<div id="content"></div>
</body>
</html>
HTML3
