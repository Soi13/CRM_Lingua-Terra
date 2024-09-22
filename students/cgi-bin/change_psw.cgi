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

######������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass))
{

my $curr_psw=$cgi->param('curr_psw');
my $new_psw=$cgi->param('new_psw');
my $new_psw1=$cgi->param('new_psw1');

$curr_psw=~s/\0//g; $curr_psw=~s/\.\.//g; $curr_psw=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$new_psw=~s/\0//g; $new_psw=~s/\.\.//g; $new_psw=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$new_psw1=~s/\0//g; $new_psw1=~s/\.\.//g; $new_psw1=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

#������� ������
$curr_psw=md5_hex($curr_psw);

#�������� �� ������������� �������� � �� �� ���������� ������ � ������
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");
my $sql="select Num_dogovor, FIO, PASSW from pupils where Num_dogovor like ? and PASSW like ?";
$sth=$dbh->prepare($sql);
$sth->execute($formLogin,$curr_psw);

#�������� ���-�� �����
my $rows_affected = $sth->rows();

#� ������ ���������� ����������� ������
my @row = $sth->fetchrow_array;

$dbh->disconnect;

#########���� ������� ����� 0, �� ������ ��� ����� ���� �� �������
if ($rows_affected==0)
{
    my $ans="������� ������ ����� �� �����!";
    #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit();
}
###################################################################


#######���� ����� ������ �� ���������, ���������� ������������.
if ($new_psw ne $new_psw1)
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
if (($new_psw!~m/((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@|#|$|%|!]).{8,20})/gm) && ($new_psw1!~m/((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@|#|$|%|!]).{8,20})/gm))
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


###########��������� ��������� �� ��������� ������ � ������� � ������� ����������� ����� �������, � ���� ���������, �� ������ UPDATE ������
if ($row[0] eq $formLogin && $row[2] eq $curr_psw)
{
  #������ ������
  my $md5_psw=md5_hex($new_psw); # ������� ������
  my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="update pupils set PASSW=? where Num_dogovor like ?";
  $sth1=$dbh1->prepare($sql1); #��� �������� ������� �� ���������� ��������
  $sth1->execute($md5_psw, $row[0]);
  $dbh1->disconnect;
  
  #������� ��������� ������ � ������� pupils, �������������� ��� �������� ��������
  my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth2=$dbh2->do("SET NAMES 'cp1251'");
  my $sql2="update pupils set TEMP_PASSW=NULL where Num_dogovor like ?";
  $sth2=$dbh2->prepare($sql2); #��� �������� ������� �� ���������� ��������
  $sth2->execute($row[0]);
  $dbh2->disconnect;

  my $ans="������ ������� �������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit();
}
##############################################################

#�������� ������
sub f_delete_session {
         #������� ����
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'https://students.linguaterra-soft.ru');
         print "Set-Cookie: $cookies\n";
         #������� ������
         $sess->delete();
         $sess->flush();
        }

}
else { print "Location: https://students.linguaterra-soft.ru\n\n"; }
#############################################################



