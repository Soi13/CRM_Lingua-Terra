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

my $page=param('page');
my $rows=param('rows');
my $sort=param('sort');
my $order=param('order');
my $n_dog=param('n_dog');
$n_dog=~s/\0//g; $n_dog=~s/\.\.//g; $n_dog=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

#���� ��� ����������, �������� � ��� �� ����� 0, �� ��������� �����
if (defined($n_dog) && length($n_dog)!=0)
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from orders where PUPILS_NUM_DOGOVOR_OR_KA like ?";
$sth=$dbh->prepare($sql);
$sth->execute($n_dog);

#� ������ ���������� ����������� ������
my @row = $sth->fetchrow_array;

my $sql1="select orders.ID, orders.TYPE_DOC, orders.DATE_PAY, orders.PUPILS_NUM_DOGOVOR_OR_KA, pupils.FIO, orders.OSNOVANIE, orders.SUMM_OPL, usr.FULL_NAME, orders.STATUS from orders, pupils, usr where PUPILS_NUM_DOGOVOR_OR_KA like ? and orders.USER_ID=usr.ID and pupils.Num_dogovor=orders.PUPILS_NUM_DOGOVOR_OR_KA limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($n_dog, $offset, $rows);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

$dbh->disconnect;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
else #����� ����� �������� �� ���������, �� ������� � �� ����� 0, �� ���������� ���� ������ �������
{
my $offset=($page-1)*$rows;

my @result;
my @res;

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from orders";
$sth=$dbh->prepare($sql);
$sth->execute();

#� ������ ���������� ����������� ������
my @row = $sth->fetchrow_array;

my $sql1="select orders.ID, orders.TYPE_DOC, orders.DATE_PAY, orders.PUPILS_NUM_DOGOVOR_OR_KA, pupils.FIO, orders.OSNOVANIE, orders.SUMM_OPL, usr.FULL_NAME, orders.STATUS from orders, pupils, usr where orders.USER_ID=usr.ID and pupils.Num_dogovor=orders.PUPILS_NUM_DOGOVOR_OR_KA limit ?,?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($offset, $rows);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

$dbh->disconnect;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}


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