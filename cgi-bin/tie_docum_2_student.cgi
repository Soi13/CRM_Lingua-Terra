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

  #������� ������ ����� ���������� �� �����
  my @form_fields=(param('TYPE_DOC'), param('COURSE'), param('TYPE_GROUP'), param('PRICE_COURSE'), param('DATE_START_DOGOVOR'), param('DATE_END_DOGOVOR'), param('TEXT_DOCUM'), param('num_dog_stud'));
  
  foreach my $el (@form_fields)
  {
      $el=~s/\0//g;
      $el=~s/\.\.//g;
      $el=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;      
  }


########�������� �� ���� ��� ���������
if (length($form_fields[0])==0)
{
  my $ans="���������� ��������� \"��� ���������\"!";
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

########�������� �� ���� ������ ���������� ����� ���������
my $dbh_tp=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_tp=$dbh_tp->do("SET NAMES 'cp1251'");

my $sql_tp="select ID from type_doc where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_tp=$dbh_tp->prepare($sql_tp);
$sth_tp->execute($form_fields[0]);
my $cnt=$sth_tp->rows();
$dbh_tp->disconnect();

if ($cnt==0)
{
  my $ans="��� ��������� ���������� �������� ������ �� ������!";
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

########�������� �� ���� �����
if (length($form_fields[1])==0)
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

########�������� �� ���� ������ ���������� ������
my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");
my $sql_br="select ID from kind_programm where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[1]);
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

########�������� �� ���� ���� ������
if (length($form_fields[2])==0)
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

########�������� �� ���� ������ ���������� ����� �����
my $dbh_br=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_br=$dbh_br->do("SET NAMES 'cp1251'");
my $sql_br="select ID from type_groups where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_br=$dbh_br->prepare($sql_br);
$sth_br->execute($form_fields[2]);
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

########�������� �� ���� �����
if (length($form_fields[3])==0)
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
if ($form_fields[3]!~m/^\d+(?:[.,]?\d+)?(\|\d+(?:[.,]?\d+)?)*$/i)
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

#�������� ������������ ���� ������ ��������
## ������, ����� ����� ��������� ��� ��� ���������: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. ��� ����� �� ���� ������� ������������ ���� � ������ (�������� ������ 12). � ������� ����, ����� ����� ���� ������������ �������������, ��� �� ����������� ���� �������� ����� ��� ����.
if ($form_fields[4]!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="��������� ���� ������ �������� �� ���������. ������ ������ ����, ��������, 2016-05-30.";
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
$form_fields[4]=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="� ��������� ���� ������ �������� �� ��������� �����. ����� �� ����� ���� ������ 12!";
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
$form_fields[4]=~/\d{4}/;
if ($&>3000)
{
        my $ans="� ��������� ���� ������ �������� �� ������� ������� ���.";
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
$form_fields[4]=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="� ��������� ���� ������ �������� �� ��������� ������ �����! ����� �� ����� ���� ����� 31!";
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

#�������� ������������ ���� ��������� ��������
## ������, ����� ����� ��������� ��� ��� ���������: (^\d{4})[-](0\d|1[012])[-]([0-2]\d|3[01])$. ��� ����� �� ���� ������� ������������ ���� � ������ (�������� ������ 12). � ������� ����, ����� ����� ���� ������������ �������������, ��� �� ����������� ���� �������� ����� ��� ����.
if ($form_fields[5]!~m/^\d{4}[-]\d{2}[-]\d{2}$/is)
{
        my $ans="��������� ���� ��������� �������� �� ���������. ������ ������ ����, ��������, 2016-05-30.";
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
$form_fields[5]=~/(?<=-)(\d{2})(?=-)/;
if ($&>12)
{
        my $ans="� ��������� ���� ��������� �������� �� ��������� �����. ����� �� ����� ���� ������ 12!";
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
$form_fields[5]=~/\d{4}/;
if ($&>3000)
{
        my $ans="� ��������� ���� ��������� �������� �� ������� ������� ���.";
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
$form_fields[5]=~/(?<=-)(\d{2})$/;
if ($&>31)
{
        my $ans="� ��������� ���� ��������� �������� �� ��������� ������ �����! ����� �� ����� ���� ����� 31!";
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
my @f = ($form_fields[4] =~ /^(\d+)\-(\d+)\-(\d+)$/);
my @e = ($form_fields[5] =~ /^(\d+)\-(\d+)\-(\d+)$/);
my $fepoch = timelocal(0,0,0,$f[2],$f[1]-1,$f[0]);
my $sepoch = timelocal(0,0,0,$e[2],$e[1]-1,$e[0]);
if ($fepoch>$sepoch)
{
  my $ans="���� ������ �������� �� ����� ���� ������ ���� ���������";
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

########�������� �� ���� �������
if (length($form_fields[6])==0)
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

########�������� �� ���� ������ ���������� ����� ���������
my $dbh_tp=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_tp=$dbh_tp->do("SET NAMES 'cp1251'");

my $sql_tp="select ID from document_templates where ID=?"; #���������� ID,�.�. combobox ��� ������ ������������ ������� ���������� ��� ID 
$sth_tp=$dbh_tp->prepare($sql_tp);
$sth_tp->execute($form_fields[6]);
my $cnt=$sth_tp->rows();
$dbh_tp->disconnect();

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


  #�������� ��� ���� (��� ����) � �������� � �������� ����������� ��������
  my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth=$dbh->do("SET NAMES 'cp1251'");
  my $sql="select * from pupils where Num_dogovor=?";
  $sth=$dbh->prepare($sql);
  $sth->execute($form_fields[7]);
  #� ������ ���������� ����������� ������
  my @row_student = $sth->fetchrow_array;
  $dbh->disconnect;

  #�������� ����� ������� ��������� �� ��������� �������� ����� ����������� ��������
  my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="select TEXT_OF_DOCUMENT from document_templates where ID=?";
  $sth1=$dbh1->prepare($sql1);
  $sth1->execute($form_fields[6]);
  #� ������ ���������� ����������� ������
  my @row_template = $sth1->fetchrow_array;
  $dbh1->disconnect;
  
  #�������� ��� ���� �� ���� ������
  my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth2=$dbh2->do("SET NAMES 'cp1251'");
  my $sql2="select * from type_groups where ID=?";
  $sth2=$dbh2->prepare($sql2);
  $sth2->execute($form_fields[2]);
  #� ������ ���������� ����������� ������
  my @row_type_group = $sth2->fetchrow_array;
  $dbh2->disconnect;
  
  #�������� ��� �����
  my $dbh3=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth3=$dbh3->do("SET NAMES 'cp1251'");
  my $sql3="select NAME_PROGRAMM from kind_programm where ID=?";
  $sth3=$dbh3->prepare($sql3);
  $sth3->execute($form_fields[1]);
  #� ������ ���������� ����������� ������
  my @row_course = $sth3->fetchrow_array;
  $dbh3->disconnect;
  
  
  my $res_price=$row_type_group[1]." - ".$row_type_group[2]."./".$row_type_group[3].". ������������: ".$row_type_group[5]; #��������� ����� ������ ��������� ��� ��������� � �������
   
  $row_template[0]=~s/%�����_��������%/$row_student[0]/ig;  
  $row_template[0]=~s/%����_������_��������%/$form_fields[4]/ig;  
  $row_template[0]=~s/%���_��������%/$row_student[1]/ig;
  $row_template[0]=~s/%���_���������%/$row_course[0]/ig;
  $row_template[0]=~s/%������_���������_�����%/$form_fields[3]/ig;
  $row_template[0]=~s/%����_���������_��������%/$form_fields[5]/ig;
  $row_template[0]=~s/%�����_��������_��������%/$row_student[10]/ig;
  $row_template[0]=~s/%�����_��������_��������%/$row_student[18]/ig;
  $row_template[0]=~s/%���_�����_�������_��������%/$row_student[19]/ig;
  $row_template[0]=~s/%�����_�����_�������_��������%/$row_student[20]/ig;
  $row_template[0]=~s/%���_�����%/$row_student[5]/ig;
  $row_template[0]=~s/%���_�������%/$row_student[6]/ig;  
  $row_template[0]=~s/%��������� ��������%/$res_price/ig;  
  $row_template[0]=~s/%���_��������_��������%/$row_student[13]/ig;  
  $row_template[0]=~s/%����_��������_��������%/$row_student[2]/ig;  
  $row_template[0]=~s/%�����_��������_��������%/$row_student[15]/ig;  
  $row_template[0]=~s/%�����_��������_��������%/$row_student[14]/ig;  
  $row_template[0]=~s/%���_�����_�������_��������%/$row_student[16]/ig;  
  $row_template[0]=~s/%�����_�����_�������_��������%/$row_student[17]/ig;  
  
  
  #��������� ������ � ��������
  my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth2=$dbh2->do("SET NAMES 'cp1251'");
  my $sql2="insert into document_students (PUPILS_Num_dogovor, TYPE_DOC, COURSE, TYPE_GROUP, PRICE_COURSE, DATE_START_DOGOVOR, DATE_END_DOGOVOR, TEXT_DOCUM, USER_ID, DATETIME_CREATE) values (?,?,?,?,?,?,?,?,?, NOW())";  
  $sth2=$dbh2->prepare($sql2); #��� �������� ������� �� ���������� ��������
  $sth2->execute($form_fields[7], $form_fields[0], $form_fields[1], $form_fields[2], $form_fields[3], $form_fields[4], $form_fields[5], $row_template[0], $us_id);    
  $dbh2->disconnect;

  #��������� �������� � ��������� ��� ���������/����, ��������� � ��������. ��� ��� ����������� ���������� �� ��������� �� ���� ��������� ��� �������� ������.
  my $dbh3=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth3=$dbh3->do("SET NAMES 'cp1251'");
  my $sql3="update pupils set KIND_PROG_FROM_DOGOVOR=? where Num_dogovor=?";  
  $sth3=$dbh3->prepare($sql3); #��� �������� ������� �� ���������� ��������
  $sth3->execute($form_fields[1], $row_student[0]);
  $dbh3->disconnect;
  
  my $ans="�������� �������� �������!";
  #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
  my $res=$ans;

  #convert  data to JSON
  my $op = JSON -> new -> pretty(1);
  my $json = $op -> encode({result => $res});

  print $cgi->header('application/json;charset=windows-1251');
  print $json;
  exit;
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
