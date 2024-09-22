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

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

my $month=param('month');
my $year=param('year');

$month=~s/\0//g; $month=~s/\.\.//g; $month=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$year=~s/\0//g; $year=~s/\.\.//g; $year=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

########�������� ������ �� ���� ������ ���� (�������� ���������� � ������)
if ($month!~m/^\d+$/i)
{
  my $ans="������������ ������ ������!";
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

########�������� ���� �� ���� ������ ����
if ($year!~m/^\d+$/i)
{
  my $ans="��� ����� �������� ������ �� ����!";
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


my $per=$month.".".$year;

my @result;
my @res;
my $cnt=0;

my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql1="select sum(pays.OPL_SUMM) as fact from pays, groups, branches where concat(month(pays.DATE_OF_PAY),'.',year(pays.DATE_OF_PAY))=? and pays.GROUP_ID=groups.ID and groups.BRANCH=branches.ID";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($per);
#� ������ ���������� ����������� ������
my @row = $sth1->fetchrow_array;


my $sql="select branches.ID as br_id, branches.BRANCH as br, sum(pays.OPL_SUMM) as fact, concat(month(pays.DATE_OF_PAY),'.',year(pays.DATE_OF_PAY)) as period from pays, groups, branches where concat(month(pays.DATE_OF_PAY),'.',year(pays.DATE_OF_PAY))=? and pays.GROUP_ID=groups.ID and groups.BRANCH=branches.ID group by branches.BRANCH";
$sth=$dbh->prepare($sql);
$sth->execute($per);

while ($data=$sth->fetchrow_hashref) {
push @result, $data;
$cnt++;
}

$dbh->disconnect;


my $cgi=CGI->new;
my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $cnt, footer => [{fact=>$row[0]." ���.", br=>"�����:"}]}  );

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");
print $json;


#�������� ������
sub f_delete_session {
         #������� ����
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'https://linguaterra-soft.ru');
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