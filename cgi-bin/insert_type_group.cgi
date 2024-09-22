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

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

my $GROUPS=param('GROUPS');
my $PRICE=param('PRICE');
my $TYPE_OPL=param('TYPE_OPL');
my $CURRENCY=param('CURRENCY');
my $DURATION=param('DURATION');
my $DIRECTION_STUDY=param('DIRECTION_STUDY');

$GROUPS=~s/\0//g; $GROUPS=~s/\.\.//g; $GROUPS=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$PRICE=~s/\0//g; $PRICE=~s/\.\.//g; $PRICE=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$TYPE_OPL=~s/\0//g; $TYPE_OPL=~s/\.\.//g; $TYPE_OPL=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$CURRENCY=~s/\0//g; $CURRENCY=~s/\.\.//g; $CURRENCY=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$DURATION=~s/\0//g; $DURATION=~s/\.\.//g; $DURATION=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$DIRECTION_STUDY=~s/\0//g; $DIRECTION_STUDY=~s/\.\.//g; $DIRECTION_STUDY=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

#�������������
Encode::from_to($GROUPS,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($TYPE_OPL,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($CURRENCY,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($DURATION,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($DIRECTION_STUDY,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
###########################

########�������� �� ���� ���� ������
if (length($GROUPS)==0)
{
  my $ans="���������� ��������� \"��� ������\"!";
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

########�������� ������ ���� ������
if (length($GROUPS)>255)
{
  my $ans="������ ������������ ���� ������ �� ����� ���� ����� 255 ��������!";
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

########�������� �� ���� ���������
if (length($PRICE)==0)
{
  my $ans="���������� ��������� \"��������� ��������\"!";
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

########�������� �� ���� ���� ������
if (length($TYPE_OPL)==0)
{
  my $ans="���������� ��������� \"��� ������\"!";
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

########�������� ������ ���� ������
if (length($TYPE_OPL)>50)
{
  my $ans="������ ������������ ���� ������ �� ����� ���� ����� 50 ��������!";
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
if (length($CURRENCY)==0)
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

########�������� �� ���� ������������ �������
if (length($DURATION)==0)
{
  my $ans="���������� ��������� \"������������ �������\"!";
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

########�������� ������ ������������ �������
if (length($DURATION)>50)
{
  my $ans="������ ������������ ������������ ������� �� ����� ���� ����� 50 ��������!";
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

########�������� ������ ����������� ��������
if (length($DIRECTION_STUDY)>150)
{
  my $ans="������ ������������ ����������� �������� �� ����� ���� ����� 150 ��������!";
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

my $show_cl=0;
if ($DIRECTION_STUDY eq "������������")
{
  $show_cl=1;
}
  
  #��������� ��� ��� ������
  my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="insert into type_groups (GROUPS, PRICE, TYPE_OPL, CURRENCY, DURATION, DIRECTION_STUDY, SHOW_COLOR, BLOCKED) values (?,?,?,?,?,?,?,0)";
  $sth1=$dbh1->prepare($sql1); #��� �������� ������� �� ���������� ��������
  $sth1->execute($GROUPS, $PRICE, $TYPE_OPL, $CURRENCY, $DURATION, $DIRECTION_STUDY, $show_cl);

  $dbh1->disconnect;

  my $ans="��� ������ �������� �������!";
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
