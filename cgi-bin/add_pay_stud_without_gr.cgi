#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
use CGI qw (:standart);
use CGI qw(:cgi);
#use CGI::Carp qw(fatalsToBrowser);
use JSON;
use ConnectDB;
use CGI::Session;
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

my $nm_dg=param('num_dg_stud_without_gr');
my $sum_pay=param('SUM_PAY_WITHOUT_GR');
my $notes=param('NOTES_PAY_WITHOUT_GR');
my $date_pay=param('DATE_PAY_WITHOUT_GR');
my $kind_opl=param('KIND_OPL_WITHOUT_GR');
my $osnovanie_opl=param('OSNOVANIE_OPL');
$nm_dg=~s/\0//g; $nm_dg=~s/\.\.//g; $nm_dg=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$sum_pay=~s/\0//g; $sum_pay=~s/\.\.//g; $sum_pay=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$notes=~s/\0//g; $notes=~s/\.\.//g; $notes=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$date_pay=~s/\0//g; $date_pay=~s/\.\.//g; $date_pay=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$kind_opl=~s/\0//g; $kind_opl=~s/\.\.//g; $kind_opl=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$osnovanie_opl=~s/\0//g; $osnovanie_opl=~s/\.\.//g; $osnovanie_opl=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

Encode::from_to($notes,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($kind_opl ,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($osnovanie_opl ,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������


#��������� �������� �� ������� � ������. ���� ��, �� ������� ������ � ������ ������������ ������ ������, ������� ����� � �������� ������.
my $dbh5=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth5=$dbh5->do("SET NAMES 'cp1251'");
my $sql5="select PUPILS_NUM_DOGOVOR from groups_students where PUPILS_NUM_DOGOVOR=?";
$sth5=$dbh5->prepare($sql5);
$sth5->execute($nm_dg);
#� ������ ���������� ����������� ������
my @stud = $sth5->fetchrow_array;
if (@stud)
{
   my$ans="������� �������� � ������. � ����� ������ ���� ����� ���������� ����������� � �������� ������� �� ����� �����, �������� \"�������\"";
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

########�������� �� ���� ����� �������
if ((length($sum_pay)==0) ||($sum_pay=='0.00'))
{
  my $ans="���������� ��������� ����� �������!";
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

########�������� �� ������������ ����� �������
if ($sum_pay!~m/^\s*\d+\.\d+\s*$/is)
{
        my $ans="��������� ����� ������� �� ���������. ������ ������ ����, ��������, 2000.00";
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

########�������� �� ���� ���� �������
if (length($date_pay)==0)
{
  my $ans="���������� ��������� ���� �������!";
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

#�������� ������������ ���� �������
## ������, ����� ����� ��������� ��� ��� ���������: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. ��� ����� �� ���� ������� ������������ ���� � ������ (�������� ������ 12). � ������� ����, ����� ����� ���� ������������ �������������, ��� �� ����������� ���� �������� ����� ��� ����.
if ($date_pay!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="��������� ���� ������� �� ���������. ������ ������ ����, ��������, 2016-05-30.";
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
$date_pay=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="� ��������� ���� ������� �� ��������� �����. ����� �� ����� ���� ������ 12!";
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
$date_pay=~/\d{4}/;
if ($&>3000)
{
        my $ans="� ��������� ���� ������� �� ������� ������� ���.";
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
$date_pay=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="� ��������� ���� ������� �� ��������� ������ �����! ����� �� ����� ���� ����� 31!";
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

########�������� �� ���� ���� ������
if (length($kind_opl)==0)
{
  my $ans="���������� ��������� ��� ������!";
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

########�������� �� ���� ������ ���������� ����� �����
my $dbh_opl=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_opl=$dbh_opl->do("SET NAMES 'cp1251'");

my $sql_opl="select KIND_OPLATA from kind_pay where KIND_OPLATA=?"; 
$sth_opl=$dbh_opl->prepare($sql_opl);
$sth_opl->execute($kind_opl);
my $cnt=$sth_opl->rows();
$dbh_opl->disconnect();

if ($cnt==0)
{
  my $ans="���� \"��� ������\" ������ ��������� ������ ������ �� ������!";
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


my $cgi=CGI->new;

#��������� ������ ��������
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");
my $sql="insert into pays_without_group (PUPILS_NUM_DOGOVOR, OPL_SUMM, DATE_OF_PAY, STATUS, NOTES, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,NOW())";
$sth=$dbh->prepare($sql);   
$sth->execute($nm_dg, $sum_pay, $date_pay, $kind_opl, $notes, $us_id);

#���������� ��������� ����� �� ������������ �������
my $dbh3=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth3=$dbh3->do("SET NAMES 'cp1251'");
my $sql3="insert into orders_without_group (TYPE_DOC, DATE_PAY, PUPILS_NUM_DOGOVOR_OR_KA, OSNOVANIE, SUMM_OPL, USER_ID, DATETIME_CREATE, STATUS) values ('��������� �����',?,?,?,?,?,NOW(),?)";
$sth3=$dbh3->prepare($sql3);   
$sth3->execute($date_pay, $nm_dg, $osnovanie_opl, $sum_pay, $us_id, $kind_opl);


$dbh->disconnect;
$dbh3->disconnect;

my $ans="������ ������� �������!"; 
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
#         #������� ������
         $sess->delete();
         $sess->flush();
        }

#���������� SID � URL-������
sub f_add_sid {
        my $url=shift();
        if ($method eq 'path') {
                if (defined($SID) && $url !~ m/SID=/) {
                        if ($url !~ m/\?/) {
                                $url.="?SID=".$SID;
                                }
                        else {
                                $url.="&SID=".$SID;
                             }
                        }
                }
                return $url;
              }
}
else { print "Location: http://localhost:6080\n\n"; }


__END__