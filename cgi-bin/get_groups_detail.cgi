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


my $id=param('id_z');

my $cgi=CGI->new;
my @res;

my $data;
my $dbh=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth=$dbh->do("SET NAMES 'cp1251'");
my $sth1=$dbh->do("SET NAMES 'cp1251'");
my $sth2=$dbh->do("SET NAMES 'cp1251'");
my $sth3=$dbh->do("SET NAMES 'cp1251'");
my $sth4=$dbh->do("SET NAMES 'cp1251'");
my $sth5=$dbh->do("SET NAMES 'cp1251'");
my $sth6=$dbh->do("SET NAMES 'cp1251'");
my $sth7=$dbh->do("SET NAMES 'cp1251'");
my $sth8=$dbh->do("SET NAMES 'cp1251'");
my $sth9=$dbh->do("SET NAMES 'cp1251'");
my $sth10=$dbh->do("SET NAMES 'cp1251'");


my $sql="select '����' as 'name', kind_languages.LANGUAGE as 'value', '��������� ����������' as 'group' from groups, kind_languages where groups.LANGUAGE=kind_languages.ID and groups.ID like ?";
my $sql1="select '�������' as 'name', level_knowledge.LEVEL as 'value', '��������� ����������' as 'group' from groups, level_knowledge where groups.LEVEL_KNOWLEDGE=level_knowledge.ID and groups.ID like ?";
my $sql2="select '���������' as 'name', kind_programm.NAME_PROGRAMM as 'value', '��������� ����������' as 'group' from groups, kind_programm where groups.KIND_PROGRAMM=kind_programm.ID and groups.ID like ?";
my $sql3="select '��� ������' as 'name', type_groups.GROUPS as 'value', '��������� ����������' as 'group' from groups, type_groups where groups.GROUP_TYPE=type_groups.ID and groups.ID like ?";
my $sql4="select '��������� �������' as 'name', type_calc_lessons.TYPE_CALC as 'value', '��������� ����������' as 'group' from groups, type_calc_lessons where groups.TYPE_CALC_LESSON=type_calc_lessons.ID and groups.ID like ?";
my $sql5="select '���-�� �������' as 'name', COUNT_CLASSES as 'value', '��������� ����������' as 'group' from groups where ID like ?";
my $sql6="select '���������. �������' as 'name', DURATION_CLASSES as 'value', '��������� ����������' as 'group' from groups where ID like ?";
my $sql7="select '���. ���-�� ���������' as 'name', MIN_COUNT_STUDENTS as 'value', '��������� ����������' as 'group' from groups where groups.ID like ?";
my $sql8="select '����. ���-�� ���������' as 'name', MAX_COUNT_STUDENTS as 'value', '��������� ����������' as 'group' from groups where groups.ID like ?";
my $sql9="select '��� �������' as 'name', type_pay.PAY as 'value', '��������� ����������' as 'group' from groups, type_pay where groups.TYPE_PAY=type_pay.ID and groups.ID like ?";
my $sql10="select '������' as 'name', branches.BRANCH as 'value', '��������� ����������' as 'group' from groups, branches where groups.BRANCH=branches.ID and groups.ID like ?";



$sth=$dbh->prepare($sql);
$sth1=$dbh->prepare($sql1);
$sth2=$dbh->prepare($sql2);
$sth3=$dbh->prepare($sql3);
$sth4=$dbh->prepare($sql4);
$sth5=$dbh->prepare($sql5);
$sth6=$dbh->prepare($sql6);
$sth7=$dbh->prepare($sql7);
$sth8=$dbh->prepare($sql8);
$sth9=$dbh->prepare($sql9);
$sth10=$dbh->prepare($sql10);

$sth->execute($id);
$sth1->execute($id);
$sth2->execute($id);
$sth3->execute($id);
$sth4->execute($id);
$sth5->execute($id);
$sth6->execute($id);
$sth7->execute($id);
$sth8->execute($id);
$sth9->execute($id);
$sth10->execute($id);


while ($data=$sth->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth1->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth2->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth3->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth4->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth5->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth6->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth7->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth8->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth9->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth10->fetchrow_hashref) {
push @res, $data;
}

$dbh->disconnect;

my $op=JSON->new->pretty(1);
my $json=$op->encode({ rows=> \@res, total => 4 });

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