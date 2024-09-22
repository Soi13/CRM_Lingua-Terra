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

my $nm_dg=param('num_dg_stud');
my $sum_pay=param('SUM_PAY');
my $notes=param('NOTES_PAY');
my $date_pay=param('DATE_PAY');
my $kind_opl=param('KIND_OPL');
$nm_dg=~s/\0//g; $nm_dg=~s/\.\.//g; $nm_dg=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$sum_pay=~s/\0//g; $sum_pay=~s/\.\.//g; $sum_pay=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$notes=~s/\0//g; $notes=~s/\.\.//g; $notes=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$date_pay=~s/\0//g; $date_pay=~s/\.\.//g; $date_pay=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$kind_opl=~s/\0//g; $kind_opl=~s/\.\.//g; $kind_opl=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

Encode::from_to($notes,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
Encode::from_to($kind_opl ,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������

########�������� �� ������� ������������ ����� � �������� ��� ����� �����
my $dbh_wp=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth_wp=$dbh_wp->do("SET NAMES 'cp1251'");

my $sql_wp="select PUPILS_NUM_DOGOVOR from pays_without_group where PUPILS_NUM_DOGOVOR=?"; 
$sth_wp=$dbh_wp->prepare($sql_wp);
$sth_wp->execute($nm_dg);
my $cnt_wp=$sth_wp->rows();
$dbh_wp->disconnect();

if ($cnt_wp>0)
{
  my $ans="������ ������� ����� ��������� ������������ ������. ����� ������ ������ ������ ���������� ��������� ������������ ������ � �������� ������ �����. ������� ��� �������� � �������� \"������������ ������\"";
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

my @row;
my @data;
my $cgi=CGI->new;

#���������� ����, ��� ��������� � ������������ ������ ��������
my $dbh4=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth4=$dbh4->do("SET NAMES 'cp1251'");
my $sql4="select kind_languages.LANGUAGE, kind_programm.NAME_PROGRAMM, groups.GROUP_NAME from kind_languages, kind_programm,groups, groups_students where kind_languages.ID=groups.LANGUAGE and kind_programm.ID=groups.KIND_PROGRAMM and groups.ID=groups_students.GROUP_ID and groups_students.PUPILS_NUM_DOGOVOR=?";
$sth4=$dbh4->prepare($sql4);
$sth4->execute($nm_dg);
my @data_stud = $sth4->fetchrow_array;

my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");
my $sql="select pupils_num_dogovor, period, summ_4_opl, opl_summ from pays where pupils_num_dogovor=? and (opl_summ=0 or summ_4_opl>opl_summ) order by (SUBSTRING_INDEX(period, '.', -1)+0), (SUBSTRING_INDEX(period, '.', 1)+0)";
$sth=$dbh->prepare($sql);
$sth->execute($nm_dg);


while (@data=$sth->fetchrow_array) {
push @row, @data;
}

my $input_summ=$sum_pay;
my $common_sum;

for (my $p=0; $p<=$#row; $p=$p+4)
{
    $common_sum=$common_sum+($row[$p+2]-$row[$p+3]);        
}

if ($input_summ>$common_sum)
{
   my $ans="�������� ������ ������, ��� �������� �������� �� ������� �����. ������� �� ���� ".$common_sum." ���., � �� ������� ".$input_summ." ���."; 
   #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
   my $res=$ans;

   #convert  data to JSON
   my $op = JSON -> new -> pretty(1);
   my $json = $op -> encode({result => $res});

   print $cgi->header('application/json;charset=windows-1251');
   print $json; 
   exit;
}



for (my $i=0; $i<=$#row; $i=$i+4)
{
     my $diff_sum=$row[$i+2]-$row[$i+3];
     
     if ($input_summ<$diff_sum)
     {         
        my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth2=$dbh2->do("SET NAMES 'cp1251'");
        my $sql2="update pays set OPL_SUMM=OPL_SUMM+?, DATE_OF_PAY=?, STATUS=?, NOTES=? where PUPILS_NUM_DOGOVOR=? and PERIOD=?";
        $sth2=$dbh2->prepare($sql2);   
        $sth2->execute($input_summ, $date_pay, $kind_opl, $notes, $row[$i], $row[$i+1]);
        last;
     }
     
     $input_summ-=$diff_sum;
     
     my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
     my $sth1=$dbh1->do("SET NAMES 'cp1251'");
     my $sql1="update pays set OPL_SUMM=?, DATE_OF_PAY=?, STATUS=?, NOTES=? where PUPILS_NUM_DOGOVOR=? and PERIOD=?";
     $sth1=$dbh1->prepare($sql1);
     $sth1->execute($row[$i+2], $date_pay, $kind_opl, $notes, $row[$i], $row[$i+1]); 
     
     if ($input_summ<$row[$i+2])
     {         
        my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth2=$dbh2->do("SET NAMES 'cp1251'");
        my $sql2="update pays set OPL_SUMM=?, DATE_OF_PAY=?, STATUS=?, NOTES=? where PUPILS_NUM_DOGOVOR=? and PERIOD=?";
        $sth2=$dbh2->prepare($sql2);   
        $sth2->execute($input_summ, $date_pay, $kind_opl, $notes, $row[$i], $row[$i+5]);
        last;
     }     
}

#���������� ��������� ����� �� ������������ �������
my $dbh3=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth3=$dbh3->do("SET NAMES 'cp1251'");
my $sql3="insert into orders (TYPE_DOC, DATE_PAY, PUPILS_NUM_DOGOVOR_OR_KA, OSNOVANIE, SUMM_OPL, USER_ID, DATETIME_CREATE, STATUS) values ('��������� �����',?,?,?,?,?,NOW(),?)";
$sth3=$dbh3->prepare($sql3);   
$sth3->execute($date_pay, $nm_dg, "��������. ����: ".$data_stud[0]." ���������: ".$data_stud[1], $sum_pay, $us_id, $kind_opl);

$dbh->disconnect;
$dbh3->disconnect;
$dbh4->disconnect;

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