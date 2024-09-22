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
#use Log::Any::Adapter ('File', 'file.log');
#use Log::Any::For::Std;

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

my $dir = $ENV{DOCUMENT_ROOT};

my $filename=param('file_bank');

if (length($filename)==0)
{
   my $ans="�� ������ ���� ��� �������!";
   #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
   my $res=$ans;
   #convert  data to JSON
   my $op = JSON -> new -> pretty(1);
   my $json = $op -> encode({result => $res});
   print $cgi->header('application/json;charset=windows-1251');
   print $json;
   exit; 
}

if ( ($filename=~m/\.\./g) || ($filename=~m/\-/gs) || ($filename=~m/\0/g) || ($filename=~m/<(?:[^>'"]*|(['"]).*?\1)*>/gs) || ($filename=~m/\//g) || ($filename=~m/\&/g) || ($filename=~m/\|/g) || ($filename=~m/\+\</g) || ($filename=~m/\>/gs) || ($filename=~m/\>\>/gs) || ($filename=~m/\+\>/gs) || ($filename =~m/^.*\//g) )
   {
    my $ans="������ ����� ����� �� ������!";
    #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
    my $res=$ans;
    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});
    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;        
   }
        
$filename=~s/\0//g; $filename=~s/\.\.//g; $filename=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$filename=~s/\///g; $filename=~s/\&//g; $filename=~s/\-//gs;
$filename=~s/\|//g; $filename=~s/\+\<//g; $filename=~s/\>//gs; $filename=~s/\>\>//gs; $filename=~s/\+\>//gs; $filename =~s/^.*\///g;


####�������, �� ������������� �� ����������� ���� �����. ���� ��, �� ������ ��������!
my $dbh5=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth5=$dbh5->do("SET NAMES 'cp1251'");
my $sql5="select FILE_NAME from imported_files where FILE_NAME=?";
$sth5=$dbh5->prepare($sql5);
$sth5->execute($filename);
my @imp_file = $sth5->fetchrow_array;
$dbh5->disconnect;

if (@imp_file)
{
   my $ans="������ ������� ����� ��� ������������ �����, ��������� ������ �� ��������!!!";
    #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
    my $res=$ans;
    #convert  data to JSON
    my $op = JSON -> new -> pretty(1);
    my $json = $op -> encode({result => $res});
    print $cgi->header('application/json;charset=windows-1251');
    print $json;
    exit;   
}
#####################################################################################


#���������� ���� �� ������
open (FILE, ">$dir//import_from_bank//$filename") || die "Can not open file! $filename!";
binmode FILE;
flock (FILE, 2);
print FILE while (<$filename>);
close FILE; #close $filename;

#��������� ���������� ���� ��� ��� ������ � ������������� �������� �� ���������.
open (FILE_OP, "<$dir//import_from_bank//$filename") || die "Can not open file! $filename!";
my @fil=<FILE_OP>;        
close (FILE_OP) or die $!;   
        
#�� ������ ������ ������ ������,�.�. � ���� ����������� ������ �� �����
foreach my $str_file (@fil)
{
   $str_file=~s/\0//g; $str_file=~s/\.\.//g; $str_file=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
   $str_file=~s/\///g; $str_file=~s/\&//g; $str_file=~s/\-//gs;
   $str_file=~s/\+\<//g; $str_file=~s/\>//gs; $str_file=~s/\>\>//gs; $str_file=~s/\+\>//gs; $str_file =~s/^.*\///g;
}

#�������� �� ������� � ������������� ����� ��������� � ������������� ��������. ���� ����� �������� ����, �� ������ ��������!
for (my $q1=0; $q1<=$#fil-1; $q1++)
{
   my @pay_stud1=split(/\|/, $fil[$q1]);   
   my $num_dogovor1=$pay_stud1[1]; #����� ��������
   
   my $dbh7=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
   my $sth7=$dbh7->do("SET NAMES 'cp1251'");
   my $sql7="select PUPILS_NUM_DOGOVOR from pays_without_group where PUPILS_NUM_DOGOVOR=?";
   $sth7=$dbh7->prepare($sql7);
   $sth7->execute($num_dogovor1);
   my @check_stud1 = $sth7->fetchrow_array;
   $dbh7->disconnect;
   
   if (@check_stud1)
   {
      my $ans="� ������������� ����� ������������ �������/�������� � ������� ���� ������������ �������. ��� ������� ���������� ��������� � �������� ������ ��������. ������ ������� ����� �� ��������!";
      #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
      my $res=$ans;
      #convert  data to JSON
      my $op = JSON -> new -> pretty(1);
      my $json = $op -> encode({result => $res});
      print $cgi->header('application/json;charset=windows-1251');
      print $json;
      
      unlink("$dir//import_from_bank//$filename"); #������� ������������ ����, ������������ �� �������, �.�. ����� ������� ������ �� ��� �� �����.
      
      exit;
   }   
   
}

#��������� ��������� � ����� �� ����������� �� �������. ���� � �������� ��� ���������� � ������� �����, �� ���� �� ��������� ���������.
for (my $q=0; $q<=$#fil-1; $q++)
{
   my @pay_stud=split(/\|/, $fil[$q]);   
   my $num_dogovor=$pay_stud[1]; #����� ��������
   
   my $dbh6=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
   my $sth6=$dbh6->do("SET NAMES 'cp1251'");
   my $sql6="select PUPILS_NUM_DOGOVOR from pays where PUPILS_NUM_DOGOVOR=?";
   $sth6=$dbh6->prepare($sql6);
   $sth6->execute($num_dogovor);
   my @check_stud = $sth6->fetchrow_array;
   $dbh6->disconnect;
   
   if (!@check_stud)
   {
      my $ans="� ������������� ����� ������������ �������/�������� � ������� ��� ���������� � ������� ��������. ������ ������� ����� �� ��������!";
      #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
      my $res=$ans;
      #convert  data to JSON
      my $op = JSON -> new -> pretty(1);
      my $json = $op -> encode({result => $res});
      print $cgi->header('application/json;charset=windows-1251');
      print $json;
      
      unlink("$dir//import_from_bank//$filename"); #������� ������������ ����, ������������ �� �������, �.�. ����� ������� ������ �� ��� �� �����.
      
      exit;
   }   
   
}

#������ ���� �� ������� (������ ������� ������� ��� ����� �� �����), ������ ��������� �� �������� � ������ ������ � ������ ����������� ������ ��������� � ����� (� ��������), ����� ����� �������� � ������
#���������� ������������� ���������� �����
my @dd;
my @row;
my @data;
my @exceed; 

for (my $el=0; $el<=$#fil-1; $el++)
{
   my @pay_str=split(/\|/, $fil[$el]);
   
   my $nm_dg=$pay_str[1]; #����� ��������
   my $sum_pay=$pay_str[3]/100; #����� �������
   
   #���������� ����, ��� ��������� � ������������ ������ ��������
   my $dbh4=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
   my $sth4=$dbh4->do("SET NAMES 'cp1251'");
   my $sql4="select kind_languages.LANGUAGE, kind_programm.NAME_PROGRAMM, groups.GROUP_NAME from kind_languages, kind_programm,groups, groups_students where kind_languages.ID=groups.LANGUAGE and kind_programm.ID=groups.KIND_PROGRAMM and groups.ID=groups_students.GROUP_ID and groups_students.PUPILS_NUM_DOGOVOR=?";
   $sth4=$dbh4->prepare($sql4);
   $sth4->execute($nm_dg);
   my @data_stud = $sth4->fetchrow_array;
   

   #�������� ������/������� �� �������� ������� ��������� �� ��������, ���� �������� �� ���������
   my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
   my $sth=$dbh->do("SET NAMES 'cp1251'");
   my $sql="select pupils_num_dogovor, period, summ_4_opl, opl_summ from pays where pupils_num_dogovor=? and (opl_summ=0 or summ_4_opl>opl_summ) order by (SUBSTRING_INDEX(period, '.', -1)+0), (SUBSTRING_INDEX(period, '.', 1)+0)";
   $sth=$dbh->prepare($sql);
   $sth->execute($nm_dg);

   #���������� ��� � ������
   while (@data=$sth->fetchrow_array)
   {
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
      push @exceed, $nm_dg, $common_sum;
   }


   #������������ ������ � �������� ����� �� ������������ ��� ������������� ��������
   for (my $i=0; $i<=$#row; $i=$i+4)
   {
        my $diff_sum=$row[$i+2]-$row[$i+3];
     
        if ($input_summ<$diff_sum)
        {         
           my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
           my $sth2=$dbh2->do("SET NAMES 'cp1251'");
           my $sql2="update pays set OPL_SUMM=OPL_SUMM+?, DATE_OF_PAY=NOW(), STATUS='������' where PUPILS_NUM_DOGOVOR=? and PERIOD=?";
           $sth2=$dbh2->prepare($sql2);   
           $sth2->execute($input_summ, $row[$i], $row[$i+1]);
           last;
        }
     
        $input_summ-=$diff_sum;
     
        my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
        my $sth1=$dbh1->do("SET NAMES 'cp1251'");
        my $sql1="update pays set OPL_SUMM=?, DATE_OF_PAY=NOW(), STATUS='������' where PUPILS_NUM_DOGOVOR=? and PERIOD=?";
        $sth1=$dbh1->prepare($sql1);
        $sth1->execute($row[$i+2], $row[$i], $row[$i+1]); 
                
        if ($input_summ<$row[$i+2])
        {   
           my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
           my $sth2=$dbh2->do("SET NAMES 'cp1251'");
           my $sql2="update pays set OPL_SUMM=?, DATE_OF_PAY=NOW(), STATUS='������' where PUPILS_NUM_DOGOVOR=? and PERIOD=?";
           $sth2=$dbh2->prepare($sql2);   
           $sth2->execute($input_summ, $row[$i], $row[$i+5]);
           last;
        }     
   }

   #���������� ��������� ����� �� ������������ �������
   my $dbh3=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
   my $sth3=$dbh3->do("SET NAMES 'cp1251'");
   my $sql3="insert into orders (TYPE_DOC, DATE_PAY, PUPILS_NUM_DOGOVOR_OR_KA, OSNOVANIE, SUMM_OPL, USER_ID, DATETIME_CREATE, STATUS) values ('��������� �����',NOW(),?,?,?,?,NOW(),'�����������')";
   $sth3=$dbh3->prepare($sql3);   
   $sth3->execute($nm_dg, "��������. ����: ".$data_stud[0]." ���������: ".$data_stud[1], $sum_pay, $us_id);
   
   #������� ������� ��� ��������� �������� � �����
   @data=();
   @row=();  
   @pay_str=();
   @data_stud=();
}

####��������� � �� ��� �������������� �����, ��� ����������� ����������� �������� �� ��������� �������� ������� �����.
my $dbh6=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth6=$dbh6->do("SET NAMES 'cp1251'");
my $sql6="insert into imported_files (FILE_NAME, DATETIME_CREATE) values (?,NOW())";
$sth6=$dbh6->prepare($sql6);   
$sth6->execute($filename);
$dbh6->disconnect;   

unlink("$dir//import_from_bank//$filename"); #������� ������������ ����, ������������ �� �������, �.�. ����� ������� ������ �� ��� �� �����.
   
if (@exceed)
{
    my $ans="������� ������������ ������, �� ������� ���������� �� �������";
   #Encode::from_to($ans,'utf8','windows-1251');  #���� �������������� ������������ ���� ������ ���������� � frontend ����� ajax � backend � ����� �������
   my $res=$ans;

   #convert  data to JSON
   my $op = JSON -> new -> pretty(1);
   my $json = $op -> encode({result => $res});
   print $cgi->header('application/json;charset=windows-1251');
   print $json;
}   
else
{
   my $ans="������� ������������ ������!";
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