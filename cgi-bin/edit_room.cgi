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

my $idd=param('id_x');

$idd=~s/\0//g; $idd=~s/\.\.//g; $idd=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

#������� ������ ����� ���������� �� �����
my @form_fields=(param('ROOM_NAME'), param('CAPACITY_ROOM'), param('ADDRESS_ROOM'), param('BRANCH'), param('DESCRIPTION'), param('LESSONS_OUT_OF_SCHOOL'));

for(my $n=0; $n<=$#form_fields; $n++ )
{
        $form_fields[$n]=~s/\0//g;
        $form_fields[$n]=~s/\.\.//g;
        $form_fields[$n]=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        Encode::from_to($form_fields[$n],'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
}



########�������� �� ���� ������������ ��������
if (length($form_fields[0])==0)
{
  my $ans="���������� ��������� \"�����/������������ ��������\"!";
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

########�������� �� ������ ������������ ��������
if (length($form_fields[0])>255)
{
  my $ans="������ ���� \"�����/������������ ��������\" �� ����� ���� ����� 255 ��������!";
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

########�������� �� ������ ����������� ��������
if (length($form_fields[1])>0)
{
  if (length($form_fields[1])>100)
  {
    my $ans="������ ���� \"����������� ��������\" �� ����� ���� ����� 100 ��������!";
    #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;
  }
}
##############################################################

########�������� �� ������ ������ ��������
if (length($form_fields[2])>0)
{
  if (length($form_fields[2])>255)
  {
    my $ans="������ ����\"����� ��������\" �� ����� ���� ����� 255 ��������!";
    #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;
  }
}
##############################################################

########�������� �� ���� �������
if (length($form_fields[3])==0)
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

########�������� �� ���� ������ ���������� ��������
my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");
my $sql_br="select ID from branches where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[3]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="������ ���������� �������� ������ �� ������!";
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



  #����������� �������
  my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="update rooms set ROOM_NAME=?, CAPACITY_ROOM=?, ADDRESS_ROOM=?, BRANCH=?, DESCRIPTION=?, LESSONS_OUT_OF_SCHOOL=? where ID=?";
  $sth1=$dbh1->prepare($sql1); #��� �������� ������� �� ���������� ��������
  $sth1->execute($form_fields[0], $form_fields[1], $form_fields[2], $form_fields[3], $form_fields[4], $form_fields[5], $idd);
  $dbh1->disconnect;
 

  my $ans="������� �������������� �������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  ############################################################



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
