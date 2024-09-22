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
my $able_del_zayavki=$sess->param('able_del_zayavki');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

my $LIST_STUD_NULL_SUMM=param('LIST_STUD_NULL_SUMM');
my $LIST_STUD=param('LIST_STUD');
$LIST_STUD_NULL_SUMM=~s/\0//g; $LIST_STUD_NULL_SUMM=~s/\.\.//g; $LIST_STUD_NULL_SUMM=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$LIST_STUD=~s/\0//g; $LIST_STUD=~s/\.\.//g; $LIST_STUD=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

if (!defined($LIST_STUD_NULL_SUMM) && !defined($LIST_STUD))
{
        my $ans="�� ������ �� ���� �� ����� ������ ��� ������������!";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit();
}

if (($LIST_STUD_NULL_SUMM==1) && ($LIST_STUD==1))
{
        my $ans="���������� ������������ ����! ���������� ������� ������ ���� ��� ������.";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit();
}

#��������� ������� ��� �������� � ����
if ($LIST_STUD_NULL_SUMM)
{
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");
my $sql="select Num_dogovor, FIO, HOME_ADDRESS from pupils";
$sth=$dbh->prepare($sql);
$sth->execute();

my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
$year=$year+1900;
$mon=$mon+1;
if (length($mon)==1) { $mon="0".$mon; }

my $file_name=$mday.$mon.reverse(substr($year,2,2)).".074";

open (REG, ">../file_4_bank/".$file_name) or die "������ ������� ����: $!";
my $cnt=0;

while ($data=$sth->fetchrow_hashref) {
print REG $data->{"Num_dogovor"}."|".$data->{"FIO"}."|".$data->{"HOME_ADDRESS"}."|1|������ �� ��������|".$mon.$year."||000|";
print REG "\n";
$cnt++;
}

print REG "=|".$cnt."|000";
close (REG) or die $!;

$dbh->disconnect;

my $ans="���� ����������� ������! <a href=\"../file_4_bank/$file_name\" download>������� ����</a>";
#Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
my $res=$ans;

#convert  data to JSON
my $op = JSON -> new -> pretty(1);
my $json = $op -> encode({result => $res});

print $cgi->header('application/json;charset=windows-1251');
print $json;
exit();
}

#��������� ����������� ������ ��� �������� � ����
if ($LIST_STUD)
{
my $ans="������ ����� �������� �� ��������!";
#Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
my $res=$ans;

#convert  data to JSON
my $op = JSON -> new -> pretty(1);
my $json = $op -> encode({result => $res});

print $cgi->header('application/json;charset=windows-1251');
print $json;
exit();
   
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
}
else { print "Location: http://localhost:6080\n\n"; }
#############################################################

__END__
