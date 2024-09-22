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
        print "Location: https://teachers.linguaterra-soft.ru\n\n";
        exit();
        }

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:spending",User=>"root", Password=>""}) or die CGI::Session->errstr();
$sess->name('SID');

#���� ������ ������
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: https://teachers.linguaterra-soft.ru\n\n";
        exit();
        }

#���� ����� ������ �������
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: https://teachers.linguaterra-soft.ru\n\n";
        exit();
        }

#���� IP �� ���������
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: https://teachers.linguaterra-soft.ru\n\n";
        exit();
        }

#����������� ���������� ����� � ������ ������������ �� ������
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $teacher_id=$sess->param('teacher_id');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

my $month=param('month');
my $year=param('year');

$month=~s/\0//g; $month=~s/\.\.//g; $month=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$year=~s/\0//g; $year=~s/\.\.//g; $year=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;



  my @result;
  my @res;
  my @row_dogovors;
  my $cnt=0;
  my $res_summ=0;

  my $dat;
  #������� ������ �� ������� ��������� � ������� ���� ������ ��������
  my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
  my $sth1=$dbh1->do("SET NAMES 'cp1251'");
  my $sql1="select distinct pays.PUPILS_NUM_DOGOVOR from pays, lessons where pays.GROUP_ID=lessons.GROUP_ID and lessons.TEACHER_ID=? order by pays.PUPILS_NUM_DOGOVOR";
  $sth1=$dbh1->prepare($sql1);
  $sth1->execute($teacher_id);
  #� ������ ���������� ����������� ������
  while ($dat=$sth1->fetchrow_array) {
  push @row_dogovors, $dat;
  }
  ################################################

  for (my $t=0; $t<=$#row_dogovors; $t++)
  {
      #���������� ��� �������� �� ��� ������ ��������
      my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
      my $sth2=$dbh2->do("SET NAMES 'cp1251'");
      my $sql2="select FIO from pupils where Num_dogovor=?";
      $sth2=$dbh2->prepare($sql2);
     $sth2->execute($row_dogovors[$t]);
      #� ������ ���������� ����������� ������
      my @fio = $sth2->fetchrow_array;
      ################################################
    
      #��������� ������������� �� ������� ����� �� ��������   
      my $dbh4=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
      my $sth4=$dbh4->do("SET NAMES 'cp1251'");
      my $sql4="select summ_4_opl - opl_summ as RES from pays where period=CONCAT(?,'.',?) and pupils_num_dogovor=?";
      $sth4=$dbh4->prepare($sql4);
      $sth4->execute($month,$year, $row_dogovors[$t]);
      my @row_debt = $sth4->fetchrow_array;
      #################################################
    
      #��������� ����� ����� ����� ��������, �� ������� ������, ��� ������� ��� � ������
      my $common_summ=$row_debt[0];

      #���� ����� ����� ������ 0, �� ����������� �� � ������ ��� ������ � DataGrid
      if ($common_summ>0)
      {
         #��������� ������ ��� ������ ��� � Datagrid
         push @result, {"nm_dg"=>$row_dogovors[$t],"fio"=>$fio[0],"summ"=>$common_summ};
       
         $cnt++;
         $res_summ=$res_summ+$common_summ;
      }
    
    
      #���������� ������ ������ �������� �����, ��� ���������
      @fio=();
      @row_debt=();
      }

  my $cgi=CGI->new;

  my $op=JSON::XS->new->pretty(1);
  my $json=$op->encode({ rows=> \@result, total => $cnt, footer => [{count=>$res_summ." ���.", name=>"����� �����:"}]});
  print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");
  print $json;
  exit();



#�������� ������
sub f_delete_session {
         #������� ����
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'https://teachers.linguaterra-soft.ru');
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
else { print "Location: https://teachers.linguaterra-soft.ru\n\n"; }

__END__