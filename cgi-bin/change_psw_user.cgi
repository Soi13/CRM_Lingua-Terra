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
use JSON;
use Encode;

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

######������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass))
{

my $id_u=$cgi->param('id_u');
my $psw1=$cgi->param('USER_PSW1');
my $psw2=$cgi->param('USER_PSW2');

$id_u=~s/\0//g; $id_u=~s/\.\.//g; $id_u=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$psw1=~s/\0//g; $psw1=~s/\.\.//g; $psw1=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$psw2=~s/\0//g; $psw2=~s/\.\.//g; $psw2=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;


#######�������� �� ���������� �������.
if ((length($psw1)==0) || (length($psw2)==0))
{
  my $ans="���� �� ������� ������! ��������� ����.";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit();
}
#######################################################

#######���� ����� ������ �� ���������, ���������� ������������.
if ($psw1 ne $psw2)
{
  my $ans="��������� ������ �� ���������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit();
}
#######################################################

######���� ������ �� �������� ������� ���������, �� ������� ��������� ������������
if (($psw1!~m/((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@|#|$|%|!]).{8,20})/gm) && ($psw2!~m/((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@|#|$|%|!]).{8,20})/gm))
{
  my $ans="��������� ������ �� ������������� ����������� ���������! ������ ������ ����� ������ �� 8 �� 20 ��������, ��������� ���� �� ���� �����, ���� ����� ��������� � ���������, � ����� ��������� ���� �� �������� (@#\$%!).";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit();
}
#######################################################


###########������ ������, �������������� ������ ���
my $md5_psw=md5_hex($psw1); # ������� ������
my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1="update usr set PASSW=? where ID like ?";
$sth1=$dbh1->prepare($sql1); #��� �������� ������� �� ���������� ��������
$sth1->execute($md5_psw, $id_u);
$dbh1->disconnect;

my $ans="������ ������� �������!";
#Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
my $res=$ans;

#convert  data to JSON
my $op = JSON -> new -> pretty(1);
my $json = $op -> encode({result => $res});

print $cgi->header('application/json;charset=windows-1251');
print $json;
exit();
##############################################################

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



