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
my $able_edit_event=$sess->param('able_edit_event');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {
        
if ($able_edit_event==1) #������� ����� �� ���������� ������������ ������������� �����������. ��������� ��� �� ���������� ����������� �� ������.
{
my $DATE_VISIT=param('date_visit');
my $KIND_EVENT=param('kind_event');
my $FEEDBACK=param('feedback');
my $id_event=param('id_event');

$DATE_VISIT=~s/\0//g; $DATE_VISIT=~s/\.\.//g;
$KIND_EVENT=~s/\0//g; $KIND_EVENT=~s/\.\.//g;
$FEEDBACK=~s/\0//g; $FEEDBACK=~s/\.\.//g;
$id_event=~s/\0//g; $id_event=~s/\.\.//g;

#�������������
Encode::from_to($FEEDBACK,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
###########################

#�������� ������������ ���� ������
## ������, ����� ����� ��������� ��� ��� ���������: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. ��� ����� �� ���� ������� ������������ ���� � ������ (�������� ������ 12). � ������� ����, ����� ����� ���� ������������ �������������, ��� �� ����������� ���� �������� ����� ��� ����.
if ($DATE_VISIT!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="��������� ���� ��������� �� ���������. ������ ������ ����, ��������, 2016-05-30.";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
        }
        
###########################################################################################################################################
# ��������� ���� �� ���� ����� � ��� � ��������� ����� ����� ���� �� ��������� �����������. �������� ����� �� ����� ���� ������ 12, ���� 31
###########################################################################################################################################
# ��������� ����� � ���������. ����� ��������� ��������� � ���������� $& ������������ ���������. 
$DATE_VISIT=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="� ��������� ���� ��������� �� ��������� �����. ����� �� ����� ���� ������ 12!";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
        
# ��������� ��� � ���������. ����� ��������� ��������� � ���������� $& ������������ ���������. 
$DATE_VISIT=~/\d{4}/;
if ($&>3000)
{
        my $ans="� ��������� ���� ��������� �� ������� ������� ���.";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
        
# ��������� ���� � ���������. ����� ��������� ��������� � ���������� $& ������������ ���������. 
$DATE_VISIT=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="� ��������� ���� ��������� �� ��������� ������ �����! ����� �� ����� ���� ����� 31!";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
        my $res=$ans;

        #convert  data to JSON
        my $op = JSON -> new -> pretty(1);
        my $json = $op -> encode({result => $res});

        print $cgi->header('application/json;charset=windows-1251');
        print $json;
        exit;
}
############################################################################################################################################

########�������� �� ���� ���� �����������
if (length($KIND_EVENT)==0)
{
  my $ans="���������� ��������� \"��� �����������\"!";
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

########�������� �� ���� ������ ���������� ����� �����������
my $dbh_ev=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_ev=$dbh_ev->do("SET NAMES 'cp1251'");
my $sql_ev="select ID from events where ID=?";  #���������� ID,�.�. combobox ��� ������ ������������ ���� ����������� ���������� ��� ID 
$sth_ev=$dbh_ev->prepare($sql_ev);
$sth_ev->execute($KIND_EVENT);
my $cnt=$sth_ev->rows();
$dbh_ev->disconnect();

if ($cnt==0)
{
  my $ans="������������ ���� ����������� ���������� �������� ������ �� ������!";
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


  
  #����������� �����������
  my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="update events_pupils set DATE_VISIT=?, KIND_EVENT=?, FEEDBACK=?, DATETIME_CREATE=NOW() where ID=?";
  $sth1=$dbh1->prepare($sql1); #��� �������� ������� �� ���������� ��������
  $sth1->execute($DATE_VISIT, $KIND_EVENT, $FEEDBACK, $id_event);

  $dbh1->disconnect;

  my $ans="����������� ��������������� �������!";
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
else
{
  my $ans="�� �� ������ ����� ������������� �����������!";
        #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;
  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
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
