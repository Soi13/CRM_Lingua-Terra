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

my $id_teacher=param('id_teacher');
$id_teacher=~s/\0//g; $id_teacher=~s/\.\.//g; $id_teacher=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

my @data;
my @teachers_students;
#���������� ��������� �� � ������� ��������, ���� ��, �� �������� ��� ������!
my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth2=$dbh2->do("SET NAMES 'cp1251'");
my $sql2="select pupils.FIO from pupils, lessons, groups_students where pupils.Num_dogovor=groups_students.PUPILS_NUM_DOGOVOR and groups_students.GROUP_ID=lessons.GROUP_ID and lessons.TEACHER_ID=?";
$sth2=$dbh2->prepare($sql2);
$sth2->execute($id_teacher);

#���������� ��� � ������
while (@data=$sth2->fetchrow_array) {
push @teachers_students, @data;
}

if (@teachers_students)
{
    my $ans="� ������������� ��������� ��������: ". join(', ', @teachers_students).". �������� ��������� ����������!";
    #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    ############################################################
    exit;
}


#���������� ��������� ������� (������������ ��� �������). ������ �� ����� ����� ��������� ������ ������
my $dbh0=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth0=$dbh0->do("SET NAMES 'cp1251'");
my $sql0="select BLOCKED from teachers where ID=?";
$sth0=$dbh0->prepare($sql0);
$sth0->execute($id_teacher);
my @state_teacher = $sth0->fetchrow_array;

my $query;
my $status;

if ($state_teacher[0]==1)
{
   $query="update teachers set BLOCKED=0, ACTIVE_ONLINE_ROOM=1 where ID=?";
   $status="�����������";
}
else
{
   $query="update teachers set BLOCKED=1, ACTIVE_ONLINE_ROOM=0 where ID=?";
   $status="�����";
}

my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1=$query;
$sth1=$dbh1->prepare($sql1); #��� �������� ������� �� ���������� ��������
$sth1->execute($id_teacher);

$dbh1->disconnect;

my $ans="������������� ".$status." �������!";
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
