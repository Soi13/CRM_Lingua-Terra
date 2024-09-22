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
use Time::Local;
use REST::Client;

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

#�������� ����� ����� � ������ ������� �� ���� "��������� �������". ������ ������ ������� ������� ������� ����������� �����, � �����-�� �� �������. ����� ������� � ������� ����� ����������� ������ ������� � ������ �� ����� ����� ����������� ������ ������������ � ����� ����� 
#� ����� ������ ��������� �� ���������� ���� "��������� �������", �.�. ��� �������� ��������� ������.

my $type_calc_lesson=param('TYPE_CALC_LESSON');
my $group_name=param('GROUP_NAME');
$type_calc_lesson=~s/\0//g; $type_calc_lesson=~s/\.\.//g; $type_calc_lesson=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$group_name=~s/\0//g; $group_name=~s/\.\.//g; $group_name=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
Encode::from_to($group_name,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������

########�������� �� ���� ��������� �������
if (length($type_calc_lesson)==0)
{
  my $ans="���������� ��������� \"��������� �������\"!";
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

########�������� �� ���� ������ ���������� �������� �������
my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from type_calc_lessons where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($type_calc_lesson);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="������ ������� ���������� �������� ������ �� ������!";
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

#################################��������� ���� �� ������������ �������� ������ ��� � ����. ���� ����, �� ���� �� ��������, �.�. ����� � ����������� ���������� �� ����� ����!
my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select GROUP_NAME from `groups` where `GROUP_NAME`=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($group_name);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt!=0)
{
  my $ans="������ � ������������� \"".$group_name."\" ��� ���������� � ����. ������������ ������������ �����������!";  
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
}
##############################################################################################################################################


#�������� �������� ��������� ����� ������ ������� ������ � � ����������� �� ����� ���������� ������� ������ � �������
###########################���� ������ ������ "�� ���-�� �����", �� ����� ID 1#####################################
if ($type_calc_lesson==1)
{
  #������� ������ ����� ���������� �� �����
  my @form_fields=(param('LANGUAGE'), param('LEVEL_KNOWLEDGE'), param('KIND_PROGRAMM'), param('GROUP_NAME'), param('GROUP_TYPE'), param('TYPE_CALC_LESSON'), param('COUNT_CLASSES'), param('DURATION_CLASSES'), param('START_DATE'), param('COURSE_PRICE'), param('MIN_COUNT_STUDENTS'), param('MAX_COUNT_STUDENTS'), param('TYPE_PAY'), param('BRANCH'));
  
  foreach my $el (@form_fields)
  {
      $el=~s/\0//g;
      $el=~s/\.\.//g;
      $el=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
      Encode::from_to($el,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  }


########�������� �� ���� ����
if (length($form_fields[0])==0)
{
  my $ans="���������� ��������� \"����\"!";
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

########�������� �� ���� ������ ���������� ����
my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from kind_languages where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[0]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="���� ���������� �������� ������ �� ������!";
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

=head
########�������� �� ���� �������
if (length($form_fields[1])==0)
{
  my $ans="���������� ��������� \"�������\"!";
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
=cut

########�������� �� ���� ������ ���������� �������
if (length($form_fields[1])>0)
{
  my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

  my $sql_br="select ID from level_knowledge where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
  $sth_br=$dbh_br->prepare($sql_br);
  $sth_br->execute($form_fields[1]);
  my $cnt=$sth_br->rows();
  $dbh_br->disconnect();

  if ($cnt==0)
  {
    my $ans="������� ���������� �������� ������ �� ������!";
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

########�������� �� ���� ���������
if (length($form_fields[2])==0)
{
  my $ans="���������� ��������� \"���������\"!";
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

my $sql_br="select ID from kind_programm where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[2]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="��������� ���������� �������� ������ �� ������!";
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

########�������� �� ���� ������������ ������
if (length($form_fields[3])==0)
{
  my $ans="���������� ��������� \"������������ ������\"!";
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

########�������� �� ������ ������������ ������
if (length($form_fields[3])>255)
{
  my $ans="������ ���� \"������������ ������\" �� ����� ���� ����� 255 ��������!";
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

########�������� �� ���� ��� ������
if (length($form_fields[4])==0)
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

########�������� �� ���� ������ ���������� ����� ������
my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from type_groups where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[4]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="��� ������ ���������� �������� ������ �� ������!";
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

########�������� �� ���� ������� �������
if (length($form_fields[5])==0)
{
  my $ans="���������� ��������� \"��������� �������\"!";
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

########�������� �� ���� ������ ���������� �������� ��������
my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from type_calc_lessons where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[5]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="���� \"��������� �������\" ������ ��������� ������ ������ �� ������!";
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

########�������� �� ���� ���-�� �������
if (length($form_fields[6])==0)
{
  my $ans="���������� ��������� \"���-�� �������\"!";
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

########�������� ���-�� ������� �� ���� ������ ����
if ($form_fields[6]!~m/^\d+$/i)
{
  my $ans="� ���� \"���-�� �������\" ���������� ������� ������ �����!";
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
if (length($form_fields[7])==0)
{
  my $ans="���������� ��������� \"����������������� �������\"!";
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

########�������� ����������������� ������� �� ���� ������ ���� (����� ��������, �� �������)
if ($form_fields[7]!~m/^\d+$/i)
{
  my $ans="� ���� \"����������������� �������\" ���������� ������� ������ �����!";
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

#�������� ������������ ���� ������
## ������, ����� ����� ��������� ��� ��� ���������: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. ��� ����� �� ���� ������� ������������ ���� � ������ (�������� ������ 12). � ������� ����, ����� ����� ���� ������������ �������������, ��� �� ����������� ���� �������� ����� ��� ����.
if ($form_fields[8]!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="��������� ���� ������ �� ���������. ������ ������ ����, ��������, 2016-05-30.";
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
$form_fields[8]=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="� ��������� ���� ������ �� ��������� �����. ����� �� ����� ���� ������ 12!";
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
$form_fields[8]=~/\d{4}/;
if ($&>3000)
{
        my $ans="� ��������� ���� ������ �� ������� ������� ���.";
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
$form_fields[8]=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="� ��������� ���� ������ �� ��������� ������ �����! ����� �� ����� ���� ����� 31!";
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

########�������� �� ���� ���� �����
if (length($form_fields[9])==0)
{
  my $ans="���������� ��������� \"���� �����\"!";
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

########�������� ���� �����. ����� ���������� ���������, ������� ��������� ���� ������� � ����� �����
if ($form_fields[9]!~m/^\d+(?:[.,]?\d+)?(\|\d+(?:[.,]?\d+)?)*$/i)
{
    my $ans="� ���� \"���� �����\" ���������� ������� ������ ����� (����� ���� �������)!";
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

########�������� ����������� ���-�� ��������� �� ���� ������ ���� (����� ��������, �� �������)
if (length($form_fields[10])>0)
{
  if ($form_fields[10]!~m/^\d+$/i)
  {
    my $ans="� ���� \"����������� ���-�� ���������\" ���������� ������� ������ �����!";
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

########�������� ������������ ���-�� ��������� �� ���� ������ ���� (����� ��������, �� �������)
if (length($form_fields[11])>0)
{
  if ($form_fields[11]!~m/^\d+$/i)
  {
    my $ans="� ���� \"������������ ���-�� ���������\" ���������� ������� ������ �����!";
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

########��������, ����� � ���� ����������� ���-�� ��������� �� ����� ������� ����� ��� � ������������
if (length($form_fields[10])>0 && length($form_fields[11])>0)
{
  if ($form_fields[11]<$form_fields[10])
  {
    my $ans="� ���� \"������������ ���-�� ���������\" ���������� ������� �������� ������ ��� � ���� \"����������� ���-�� ���������\"!";
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

########�������� �� ���� ���� �������
if (length($form_fields[12])==0)
{
  my $ans="���������� ��������� \"��� �������\"!";
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

########�������� �� ���� ������ ���������� ����� �������
my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from type_pay where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[12]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="���� \"��� �������\" ������ ��������� ������ ������ �� ������!";
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

########�������� �� ���� �������
if (length($form_fields[13])==0)
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
$sth_br->execute($form_fields[13]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="���� \"������\" ������ ��������� ������ ������ �� ������!";
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

  #��������� ������
  my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="insert into groups (LANGUAGE, LEVEL_KNOWLEDGE, KIND_PROGRAMM, GROUP_NAME, GROUP_TYPE, TYPE_CALC_LESSON, COUNT_CLASSES, DURATION_CLASSES, START_DATE, COURSE_PRICE, MIN_COUNT_STUDENTS, MAX_COUNT_STUDENTS, TYPE_PAY, BRANCH, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, NOW())";  
  $sth1=$dbh1->prepare($sql1); #��� �������� ������� �� ���������� ��������
  $sth1->execute($form_fields[0], $form_fields[1], $form_fields[2], $form_fields[3], $form_fields[4], $form_fields[5], $form_fields[6], $form_fields[7], $form_fields[8], $form_fields[9], $form_fields[10], $form_fields[11], $form_fields[12], $form_fields[13], $us_id);
  
      
  $dbh1->disconnect;

  my $ans="������ ��������� �������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
  ############################################################
}
###################����� ������ ������ "�� ���-�� �����", �� ����� ID 1########################################



###################���� ������ ������ "�� ���-�� �������", �� ����� ID 2
if ($type_calc_lesson==2)
{
  #������� ������ ����� ���������� �� �����
  my @form_fields=(param('LANGUAGE'), param('LEVEL_KNOWLEDGE'), param('KIND_PROGRAMM'), param('GROUP_NAME'), param('GROUP_TYPE'), param('TYPE_CALC_LESSON'), param('COUNT_CLASSES'), param('START_DATE'), param('COURSE_PRICE'), param('MIN_COUNT_STUDENTS'), param('MAX_COUNT_STUDENTS'), param('TYPE_PAY'), param('BRANCH'));
  
  foreach my $el (@form_fields)
  {
      $el=~s/\0//g;
      $el=~s/\.\.//g;
      $el=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
      Encode::from_to($el,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  }


########�������� �� ���� ����
if (length($form_fields[0])==0)
{
  my $ans="���������� ��������� \"����\"!";
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

########�������� �� ���� ������ ���������� ����
my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from kind_languages where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[0]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="���� ���������� �������� ������ �� ������!";
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

=head
########�������� �� ���� �������
if (length($form_fields[1])==0)
{
  my $ans="���������� ��������� \"�������\"!";
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
=cut

########�������� �� ���� ������ ���������� �������
if (length($form_fields[1])>0)
{
  my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

  my $sql_br="select ID from level_knowledge where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
  $sth_br=$dbh_br->prepare($sql_br);
  $sth_br->execute($form_fields[1]);
  my $cnt=$sth_br->rows();
  $dbh_br->disconnect();

  if ($cnt==0)
  {
    my $ans="������� ���������� �������� ������ �� ������!";
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

########�������� �� ���� ���������
if (length($form_fields[2])==0)
{
  my $ans="���������� ��������� \"���������\"!";
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

my $sql_br="select ID from kind_programm where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[2]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="��������� ���������� �������� ������ �� ������!";
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

########�������� �� ���� ������������ ������
if (length($form_fields[3])==0)
{
  my $ans="���������� ��������� \"������������ ������\"!";
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

########�������� �� ������ ������������ ������
if (length($form_fields[3])>255)
{
  my $ans="������ ���� \"������������ ������\" �� ����� ���� ����� 255 ��������!";
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

########�������� �� ���� ��� ������
if (length($form_fields[4])==0)
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

########�������� �� ���� ������ ���������� ����� ������
my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from type_groups where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[4]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="��� ������ ���������� �������� ������ �� ������!";
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

########�������� �� ���� ������� �������
if (length($form_fields[5])==0)
{
  my $ans="���������� ��������� \"��������� �������\"!";
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

########�������� �� ���� ������ ���������� �������� ��������
my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from type_calc_lessons where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[5]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="���� \"��������� �������\" ������ ��������� ������ ������ �� ������!";
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

########�������� �� ���� ���-�� �������
if (length($form_fields[6])==0)
{
  my $ans="���������� ��������� \"���-�� �������\"!";
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

########�������� ���-�� ������� �� ���� ������ ����
if ($form_fields[6]!~m/^\d+$/i)
{
  my $ans="� ���� \"���-�� �������\" ���������� ������� ������ �����!";
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

#�������� ������������ ���� ������
## ������, ����� ����� ��������� ��� ��� ���������: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. ��� ����� �� ���� ������� ������������ ���� � ������ (�������� ������ 12). � ������� ����, ����� ����� ���� ������������ �������������, ��� �� ����������� ���� �������� ����� ��� ����.
if ($form_fields[7]!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="��������� ���� ������ �� ���������. ������ ������ ����, ��������, 2016-05-30.";
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
$form_fields[7]=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="� ��������� ���� ������ �� ��������� �����. ����� �� ����� ���� ������ 12!";
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
$form_fields[7]=~/\d{4}/;
if ($&>3000)
{
        my $ans="� ��������� ���� ������ �� ������� ������� ���.";
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
$form_fields[7]=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="� ��������� ���� ������ �� ��������� ������ �����! ����� �� ����� ���� ����� 31!";
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

########�������� �� ���� ���� �����
if (length($form_fields[8])==0)
{
  my $ans="���������� ��������� \"���� �����\"!";
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

########�������� ���� �����. ����� ���������� ���������, ������� ��������� ���� ������� � ����� �����
if ($form_fields[8]!~m/^\d+(?:[.,]?\d+)?(\|\d+(?:[.,]?\d+)?)*$/i)
{
    my $ans="� ���� \"���� �����\" ���������� ������� ������ ����� (����� ���� �������)!";
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

########�������� ����������� ���-�� ��������� �� ���� ������ ���� (����� ��������, �� �������)
if (length($form_fields[9])>0)
{
  if ($form_fields[9]!~m/^\d+$/i)
  {
    my $ans="� ���� \"����������� ���-�� ���������\" ���������� ������� ������ �����!";
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

########�������� ������������ ���-�� ��������� �� ���� ������ ���� (����� ��������, �� �������)
if (length($form_fields[10])>0)
{
  if ($form_fields[10]!~m/^\d+$/i)
  {
    my $ans="� ���� \"������������ ���-�� ���������\" ���������� ������� ������ �����!";
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

########��������, ����� � ���� ����������� ���-�� ��������� �� ����� ������� ����� ��� � ������������
if (length($form_fields[9])>0 && length($form_fields[10])>0)
{
  if ($form_fields[10]<$form_fields[9])
  {
    my $ans="� ���� \"������������ ���-�� ���������\" ���������� ������� �������� ������ ��� � ���� \"����������� ���-�� ���������\"!";
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

########�������� �� ���� ���� �������
if (length($form_fields[11])==0)
{
  my $ans="���������� ��������� \"��� �������\"!";
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

########�������� �� ���� ������ ���������� ����� �������
my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from type_pay where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[11]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="���� \"��� �������\" ������ ��������� ������ ������ �� ������!";
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

########�������� �� ���� �������
if (length($form_fields[12])==0)
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
$sth_br->execute($form_fields[12]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="���� \"������\" ������ ��������� ������ ������ �� ������!";
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


  #��������� ������
  my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="insert into groups (LANGUAGE, LEVEL_KNOWLEDGE, KIND_PROGRAMM, GROUP_NAME, GROUP_TYPE, TYPE_CALC_LESSON, COUNT_CLASSES, START_DATE, COURSE_PRICE, MIN_COUNT_STUDENTS, MAX_COUNT_STUDENTS, TYPE_PAY, BRANCH, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?, NOW())";  
  $sth1=$dbh1->prepare($sql1); #��� �������� ������� �� ���������� ��������
  $sth1->execute($form_fields[0], $form_fields[1], $form_fields[2], $form_fields[3], $form_fields[4], $form_fields[5], $form_fields[6], $form_fields[7], $form_fields[8], $form_fields[9], $form_fields[10], $form_fields[11], $form_fields[12], $us_id);
        
  $dbh1->disconnect;

  my $ans="������ ��������� �������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
  ############################################################
}
###################����� ������ ������ "�� ���-�� �������", �� ����� ID 2########################################




###################���� ������ ������ "�� ���� ���������", �� ����� ID 3
if ($type_calc_lesson==3)
{
  #������� ������ ����� ���������� �� �����
  my @form_fields=(param('LANGUAGE'), param('LEVEL_KNOWLEDGE'), param('KIND_PROGRAMM'), param('GROUP_NAME'), param('GROUP_TYPE'), param('TYPE_CALC_LESSON'), param('START_DATE'), param('END_DATE'), param('COURSE_PRICE'), param('MIN_COUNT_STUDENTS'), param('MAX_COUNT_STUDENTS'), param('TYPE_PAY'), param('BRANCH'));
  
  foreach my $el (@form_fields)
  {
      $el=~s/\0//g;
      $el=~s/\.\.//g;
      $el=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
      Encode::from_to($el,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  }


########�������� �� ���� ����
if (length($form_fields[0])==0)
{
  my $ans="���������� ��������� \"����\"!";
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

########�������� �� ���� ������ ���������� ����
my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from kind_languages where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[0]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="���� ���������� �������� ������ �� ������!";
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

=head
########�������� �� ���� �������
if (length($form_fields[1])==0)
{
  my $ans="���������� ��������� \"�������\"!";
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
=cut

########�������� �� ���� ������ ���������� �������
if (length($form_fields[1])>0)
{
  my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

  my $sql_br="select ID from level_knowledge where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
  $sth_br=$dbh_br->prepare($sql_br);
  $sth_br->execute($form_fields[1]);
  my $cnt=$sth_br->rows();
  $dbh_br->disconnect();

  if ($cnt==0)
  {
    my $ans="������� ���������� �������� ������ �� ������!";
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

########�������� �� ���� ���������
if (length($form_fields[2])==0)
{
  my $ans="���������� ��������� \"���������\"!";
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

my $sql_br="select ID from kind_programm where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[2]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="��������� ���������� �������� ������ �� ������!";
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

########�������� �� ���� ������������ ������
if (length($form_fields[3])==0)
{
  my $ans="���������� ��������� \"������������ ������\"!";
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

########�������� �� ������ ������������ ������
if (length($form_fields[3])>255)
{
  my $ans="������ ���� \"������������ ������\" �� ����� ���� ����� 255 ��������!";
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

########�������� �� ���� ��� ������
if (length($form_fields[4])==0)
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

########�������� �� ���� ������ ���������� ����� ������
my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from type_groups where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[4]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="��� ������ ���������� �������� ������ �� ������!";
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

########�������� �� ���� ������� �������
if (length($form_fields[5])==0)
{
  my $ans="���������� ��������� \"��������� �������\"!";
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

########�������� �� ���� ������ ���������� �������� �������
my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from type_calc_lessons where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[5]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="���� \"��������� �������\" ������ ��������� ������ ������ �� ������!";
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

#�������� ������������ ���� ������
## ������, ����� ����� ��������� ��� ��� ���������: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. ��� ����� �� ���� ������� ������������ ���� � ������ (�������� ������ 12). � ������� ����, ����� ����� ���� ������������ �������������, ��� �� ����������� ���� �������� ����� ��� ����.
if ($form_fields[6]!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="��������� ���� ������ �� ���������. ������ ������ ����, ��������, 2016-05-30.";
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
$form_fields[6]=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="� ��������� ���� ������ �� ��������� �����. ����� �� ����� ���� ������ 12!";
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
$form_fields[6]=~/\d{4}/;
if ($&>3000)
{
        my $ans="� ��������� ���� ������ �� ������� ������� ���.";
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
$form_fields[6]=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="� ��������� ���� ������ �� ��������� ������ �����! ����� �� ����� ���� ����� 31!";
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

#�������� ������������ ���� ���������
## ������, ����� ����� ��������� ��� ��� ���������: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. ��� ����� �� ���� ������� ������������ ���� � ������ (�������� ������ 12). � ������� ����, ����� ����� ���� ������������ �������������, ��� �� ����������� ���� �������� ����� ��� ����.
if ($form_fields[7]!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="��������� ���� ������ �� ���������. ������ ������ ����, ��������, 2016-05-30.";
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
$form_fields[7]=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="� ��������� ���� ������ �� ��������� �����. ����� �� ����� ���� ������ 12!";
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
$form_fields[7]=~/\d{4}/;
if ($&>3000)
{
        my $ans="� ��������� ���� ������ �� ������� ������� ���.";
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
$form_fields[7]=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="� ��������� ���� ������ �� ��������� ������ �����! ����� �� ����� ���� ����� 31!";
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

########��������� ���, ����� ������������ �������� �� ���� ���� ������ ������ ���� ���������
my @f = ($form_fields[6] =~ /^(\d+)\-(\d+)\-(\d+)$/);
my @e = ($form_fields[7] =~ /^(\d+)\-(\d+)\-(\d+)$/);
my $fepoch = timelocal(0,0,0,$f[2],$f[1]-1,$f[0]);
my $sepoch = timelocal(0,0,0,$e[2],$e[1]-1,$e[0]);
if ($fepoch>$sepoch)
{
  my $ans="���� ������ �� ����� ���� ������ ���� ���������";
    #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
    my $res=$ans;

    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});

    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;
}
############################################################################################

########�������� �� ���� ���� �����
if (length($form_fields[8])==0)
{
  my $ans="���������� ��������� \"���� �����\"!";
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

########�������� ���� �����. ����� ���������� ���������, ������� ��������� ���� ������� � ����� �����
if ($form_fields[8]!~m/^\d+(?:[.,]?\d+)?(\|\d+(?:[.,]?\d+)?)*$/i)
{
    my $ans="� ���� \"���� �����\" ���������� ������� ������ ����� (����� ���� �������)!";
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

########�������� ����������� ���-�� ��������� �� ���� ������ ���� (����� ��������, �� �������)
if (length($form_fields[9])>0)
{
  if ($form_fields[9]!~m/^\d+$/i)
  {
    my $ans="� ���� \"����������� ���-�� ���������\" ���������� ������� ������ �����!";
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

########�������� ������������ ���-�� ��������� �� ���� ������ ���� (����� ��������, �� �������)
if (length($form_fields[10])>0)
{
  if ($form_fields[10]!~m/^\d+$/i)
  {
    my $ans="� ���� \"������������ ���-�� ���������\" ���������� ������� ������ �����!";
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

########��������, ����� � ���� ����������� ���-�� ��������� �� ����� ������� ����� ��� � ������������
if (length($form_fields[9])>0 && length($form_fields[10])>0)
{
  if ($form_fields[10]<$form_fields[9])
  {
    my $ans="� ���� \"������������ ���-�� ���������\" ���������� ������� �������� ������ ��� � ���� \"����������� ���-�� ���������\"!";
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

########�������� �� ���� ���� �������
if (length($form_fields[11])==0)
{
  my $ans="���������� ��������� \"��� �������\"!";
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

########�������� �� ���� ������ ���������� ����� �������
my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");

my $sql_br="select ID from type_pay where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[11]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="���� \"��� �������\" ������ ��������� ������ ������ �� ������!";
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

########�������� �� ���� �������
if (length($form_fields[12])==0)
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
$sth_br->execute($form_fields[12]);
my $cnt=$sth_br->rows();
$dbh_br->disconnect();

if ($cnt==0)
{
  my $ans="���� \"������\" ������ ��������� ������ ������ �� ������!";
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


  #��������� ������
  my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="insert into `groups` (`LANGUAGE`, `LEVEL_KNOWLEDGE`, `KIND_PROGRAMM`, `GROUP_NAME`, `GROUP_TYPE`, `TYPE_CALC_LESSON`, `START_DATE`, `END_DATE`, `COURSE_PRICE`, `MIN_COUNT_STUDENTS`, `MAX_COUNT_STUDENTS`, `TYPE_PAY`, `BRANCH`, `USER_ID`, `DATETIME_CREATE`) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?, NOW())";  
  $sth1=$dbh1->prepare($sql1); #��� �������� ������� �� ���������� ��������
  $sth1->execute($form_fields[0], $form_fields[1], $form_fields[2], $form_fields[3], $form_fields[4], $form_fields[5], $form_fields[6], $form_fields[7], $form_fields[8], $form_fields[9], $form_fields[10], $form_fields[11], $form_fields[12], $us_id);
        
  $dbh1->disconnect;
  
  #######���������� ������ ��� ������ � REST ��������� ��� ������� � ������ ������
  #������������ � ������ � �������� SID, ����� � ���������� � ������� ���� ��������� ����� ������
  my $client_rest = REST::Client->new();
  $client_rest->GET('http://46.180.119.231:5533/webapi/auth.cgi?api=SYNO.API.Auth&version=3&method=login&account=LinguaPlatform&passwd=Lingua2021!&session=FileStation&format=sid');
  my $res_json = JSON->new->utf8->decode($client_rest->responseContent());
  my $sid_cloud=$res_json->{'data'}->{'sid'};
  
  #������� ����� �� ������
  my $client_folder = REST::Client->new();
  $client_folder->GET('http://46.180.119.231:5533/webapi/entry.cgi?api=SYNO.FileStation.CreateFolder&version=2&method=create&folder_path=%5B%22%2FLinguaPlatform%22%5D&name=%5B%22'.$form_fields[3].'%22%5D&_sid='.$sid_cloud);
  $client_folder->responseContent();

  my $ans="������ ��������� �������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
  ############################################################
}
###################����� ������ ������ "�� ���� ���������", �� ����� ID 3########################################


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
