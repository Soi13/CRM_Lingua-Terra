#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI::Session;
use CGI qw(:cgi);
use ConnectDB;
use JSON;
use Encode;
use Net::SMTP;
use Net::SMTP_auth;
use Date::Calc qw(:all);


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
my $teacher_id=$sess->param('teacher_id');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) { 
#������� ������ ����� ���������� �� �����

my @form_fields=(param('TOPIC_MESSAGE'), param('TEXT_OF_DOCUMENT'));

foreach my $n (@form_fields)
{
        $n=~s/\0//g;
        $n=~s/\.\.//g;
        $n=~s/<script>(.*[\s\S]*?)\<\/script>//gs; #�������� ������ ����� ������ Script
        $n=~s/<script>|<\/script>|script|\/script//gs; #�������� ����� ����� Script
        Encode::from_to($n,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
}

########�������� �� ���� ���� ���������
if (length($form_fields[0])==0)
{
  my $ans="���������� ��������� ���� \"���� ���������\"!";
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




########�������� �� ����� ������ ���������
if (length($form_fields[1])==0)
{
  my $ans="���������� ��������� ���� \"����� ���������\"!";
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


#���������� ��� ������� �� ��� ID
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");
my $sql="select FIO from teachers where ID=?";
$sth=$dbh->prepare($sql);
$sth->execute($teacher_id);
#� ������ ���������� ����������� ������
my @teacher_fio = $sth->fetchrow_array;

#��������� ��������� � ��
my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1="insert into support_messages (TOPIC, TEXT_MESSAGE, USER_ID, DATETIME_CREATE) values (?,?,?, NOW())";
$sth1=$dbh1->prepare($sql1); #��� �������� ������� �� ���������� ��������
$sth1->execute($teacher_fio[0]." - ".$form_fields[0], $form_fields[1], $teacher_id);
$dbh1->disconnect;


my $smtp = Net::SMTP_auth->new('smtp.lingua-terra.ru', Timeout => 20, Debug => 1, Port=>587) or die "Couldn't connect to server; $!"; 
$smtp->auth('LOGIN','robot@lingua-terra.ru','lingua');
$smtp->mail('robot@lingua-terra.ru');
my @to = qw(skvortsov@lingua-terra.ru);
foreach my $rcpt (@to)
{
$smtp->to($rcpt);
}
$smtp->data();
$smtp->datasend("Subject: ".$teacher_fio[0]." - ".$form_fields[0]."\n");
$smtp->datasend("To: skvortsov\@lingua-terra.ru\n");
$smtp->datasend("From: robot\@lingua-terra.ru\n");
$smtp->datasend("Content-Type: text/html; charset=\"windows-1251\"\n\n");
$smtp->datasend("\n");
$smtp->datasend($form_fields[1]);
$smtp->datasend("\n");
$smtp->quit;


  my $ans="��������� ���������� �������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;


  
#�������� ������
sub f_delete_session {
         #������� ����
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://teachers.localhost:6080');
         print "Set-Cookie: $cookies\n";
         #������� ������
         $sess->delete();
         $sess->flush();
        }

}
else { print "Location: http://teachers.localhost:6080\n\n"; }
#############################################################
__END__
