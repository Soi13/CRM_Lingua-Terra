#!/usr/bin/perl -w
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

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:a0018982_fin",User=>"a0018982_oleg", Password=>""}) or die CGI::Session->errstr();
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

my @result;
my @res;

#���������� ID ������
my $dbh2=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth2=$dbh2->do("SET NAMES 'cp1251'");
my $sql2="select GROUP_ID from groups_students where PUPILS_NUM_DOGOVOR=?";
$sth2=$dbh2->prepare($sql2);
$sth2->execute($num_dog);
my @row_dat = $sth2->fetchrow_array;
#################################################

my $cgi=CGI->new;
my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");

my $sql="select COUNT(*) from topic_homework where GROUP_ID=?";
$sth=$dbh->prepare($sql);
$sth->execute($row_dat[0]);

#� ������ ���������� ����������� ������
my @row = $sth->fetchrow_array;

my $sql1="select * from topic_homework where GROUP_ID=?";
my $sth1=$dbh->prepare($sql1);
$sth1->execute($row_dat[0]);

while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
}

$dbh->disconnect;

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, total => $row[0] });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();



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