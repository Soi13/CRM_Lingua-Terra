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
        print "Location: https://students.linguaterra-soft.ru\n\n";
        exit();
        }

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:spending",User=>"root", Password=>""}) or die CGI::Session->errstr();
$sess->name('SID');

#���� ������ ������
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: https://students.linguaterra-soft.ru\n\n";
        exit();
        }

#���� ����� ������ �������
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: https://students.linguaterra-soft.ru\n\n";
        exit();
        }

#���� IP �� ���������
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: https://students.linguaterra-soft.ru\n\n";
        exit();
        }

#����������� ���������� ����� � ������ ������������ �� ������
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $num_dog=$sess->param('stud_num_dog');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

my $cgi=CGI->new;
my @res;


#���������� ������������ ������ � ��������� �����
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");
my $sql="select groups.GROUP_NAME, groups_students.PRICE_COURSE from groups, groups_students where groups.ID=groups_students.GROUP_ID and groups_students.PUPILS_NUM_DOGOVOR=?";
$sth=$dbh->prepare($sql);
$sth->execute($num_dog);
my @row_dat = $sth->fetchrow_array;
#################################################

#��������� ������������� �� ���������� ������ �� ��������. ����� � ������� ������������ ��������� �������� � ����� ������. ������ ����� � ��� ������������ ����� ������, �������� 11.2016 � 12.2016 ������������ ������� 201611 � 201612 � �� �������������� ����������
my $data1;
my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1="select SUM(summ_4_opl- opl_summ) as RES_SUMM from pays where SUBSTRING_INDEX(period, '.', 1)<month(now()) and SUBSTRING_INDEX(period, '.', -1)<=year(now()) and pupils_num_dogovor=? and (summ_4_opl>opl_summ or opl_summ<1)";
#my $sql1="select SUM(summ_4_opl- opl_summ) as RES_SUMM from pays where concat(SUBSTRING_INDEX(period, '.', -1),SUBSTRING_INDEX(period, '.', 1))<concat(year(now()),month(now())) and pupils_num_dogovor=? and (summ_4_opl>opl_summ or opl_summ<1)";
$sth1=$dbh1->prepare($sql1);
$sth1->execute($num_dog);
my @row_debt_prev_per = $sth1->fetchrow_array;
#################################################

#��������� ������������� �� ������� ����� �� ��������
my $data2;
my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth2=$dbh2->do("SET NAMES 'cp1251'");
my $sql2="select summ_4_opl - opl_summ as RES from pays where period=CONCAT(month(now()),'.',year(now())) and pupils_num_dogovor=?";
$sth2=$dbh2->prepare($sql2);
$sth2->execute($num_dog);
my @row_debt_present_per = $sth2->fetchrow_array;
#################################################

#��������� ���������� ����� �� ���������� � ������� ������� (����� �������� �� �������� �����/������) 
my $data3;
my $dbh3=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth3=$dbh3->do("SET NAMES 'cp1251'");
my $sql3="select SUM(opl_summ) as RES from pays where pupils_num_dogovor=? and (opl_summ is not NULL and opl_summ >0)";
$sth3=$dbh3->prepare($sql3);
$sth3->execute($num_dog);
my @row_paid = $sth3->fetchrow_array;
#################################################

#��������� ����� ����� ����� ��������, �� ������� ������, ��� ������ � ���� �������� �������
my $common_summ=$row_debt_prev_per[0]+$row_debt_present_per[0];

#��������� ����� ����� ����� �������� �� ���� ����
my $common_summ_debt=$row_dat[1]-$row_paid[0];


#������������ ������� ������ ��������� ������ ��������� �����
my $proc_stud=int($row_paid[0]*100/$row_dat[1]);

if (@row_dat)
{
  my $op=JSON->new->pretty(1);
  #my $json=$op->encode(@res);
  my $json=$op->encode({result => $row_dat[0]." - ".$row_dat[1]." ���.", proc => $proc_stud, summ_debt => $common_summ_debt, summ_debt_curr_per => $common_summ});

  print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");
  print $json;
}

#�������� ������
sub f_delete_session {
         #������� ����
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'https://students.linguaterra-soft.ru');
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
else { print "Location: https://students.linguaterra-soft.ru\n\n"; }

__END__