#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
#use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI::Session;
use CGI qw(:cgi);
use ConnectDB;
use JSON;
use Encode;
use Digest::MD5 qw(md5_hex);


my $cgi = CGI->new;
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
my $us_id=$sess->param('USER_ID');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

my $SMS_GATE_LOGIN=param('SMS_GATE_LOGIN');
my $SMS_GATE_PSW=param('SMS_GATE_PSW');

$SMS_GATE_LOGIN=~s/\0//g; $SMS_GATE_LOGIN=~s/\.\.//g; $SMS_GATE_LOGIN=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$SMS_GATE_PSW=~s/\0//g; $SMS_GATE_PSW=~s/\.\.//g; $SMS_GATE_PSW=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

#�������������
Encode::from_to($SMS_GATE_LOGIN, 'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($SMS_GATE_PSW, 'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
###########################

########�������� �� ���� ������
if (length($SMS_GATE_LOGIN)==0)
{
  my $ans="���������� ��������� \"�����\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########�������� ������ ������
if (length($SMS_GATE_LOGIN)>50)
{
  my $ans="����� �� ����� ���� ������� 50 ��������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########�������� �� ���� ������
if (length($SMS_GATE_PSW)==0)
{
  my $ans="���������� ��������� \"������\"!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################

########�������� �� ������ ������
if (length($SMS_GATE_PSW)>100)
{
  my $ans="\"������\" �� ����� ���� ������� 100 ��������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################


#����������, ���� �� ��� ����������� ������ SMS ����� � �������. ���� ����, �� ������ ��������� ������, ���� ��� � ������� �����, �� ��������� ���� ������.
my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1="select * from sms_gate";
$sth1=$dbh1->prepare($sql1);
$sth1->execute();
#� ������ ���������� ����������� ������
my @row_gate = $sth1->fetchrow_array;
$dbh1->disconnect;
################################################

if (!@row_gate)
{
  #��������� ������ SMS - �����
  my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth2=$dbh2->do("SET NAMES 'cp1251'");
  my $sql2="insert into sms_gate (LOGIN, PASSW) values (?,?)";
  $sth2=$dbh2->prepare($sql2); #��� �������� ������� �� ���������� ��������
  $sth2->execute($SMS_GATE_LOGIN, $SMS_GATE_PSW);
  $dbh2->disconnect;      
  
}
else
{
  #��������� ������ SMS - �����
  my $dbh3=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth3=$dbh3->do("SET NAMES 'cp1251'");
  my $sql3="update sms_gate set LOGIN=?, PASSW=?";
  $sth3=$dbh3->prepare($sql3); #��� �������� ������� �� ���������� ��������
  $sth3->execute($SMS_GATE_LOGIN, $SMS_GATE_PSW);
  $dbh3->disconnect;      
  
}  
  
my $ans="������ ��������� �������!";
#Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
my $res=$ans;

#convert  data to JSON
my $op = JSON -> new -> pretty(1);
my $json = $op -> encode({result => $res});

print $cgi->header('application/json;charset=windows-1251');
print $json;
############################################################
exit;


#�������� ������
sub f_delete_session {
         #������� ����
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://localhost:6080');
         print "Set-Cookie: $cookies\n";
         #������� ������
         $sess->delete();
         $sess->flush();
        }

}
else { print "Location: http://localhost:6080\n\n"; }
#############################################################

__END__
