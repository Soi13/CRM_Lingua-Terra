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

my $fio=param('fio');
my $n_dogovor=param('n_dogovor');
my $teacher=param('teacher');
my $programm=param('programm');
my $branch=param('branch');
$fio=~s/\0//g; $fio=~s/\.\.//g; $fio=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$n_dogovor=~s/\0//g; $n_dogovor=~s/\.\.//g; $n_dogovor=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$teacher=~s/\0//g; $teacher=~s/\.\.//g; $teacher=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$programm=~s/\0//g; $programm=~s/\.\.//g; $programm=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$branch=~s/\0//g; $branch=~s/\.\.//g; $branch=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

Encode::from_to($fio,'utf8','windows-1251');

if (defined($teacher) && length($teacher)!=0)
{
my $cnt=0;
my @result;

my $cgi=CGI->new;
my $data;
my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1="select pupils.Num_dogovor as nm_dg, pupils.FIO as fio_student, teachers.FIO as fio_teacher, kind_programm.NAME_PROGRAMM as prog, branches.BRANCH as br from pupils, pays, groups, kind_programm, lessons, teachers, branches where pupils.Num_dogovor=pays.PUPILS_NUM_DOGOVOR and pays.GROUP_ID=groups.ID and kind_programm.ID=groups.KIND_PROGRAMM and lessons.GROUP_ID=groups.ID and lessons.TEACHER_ID=teachers.ID and pupils.BRANCH=branches.ID and teachers.ID=? group by pupils.FIO order by pupils.FIO";
$sth1=$dbh1->prepare($sql1);
$sth1->execute($teacher);
#� ������ ���������� ����������� ������
while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
$cnt++;
}

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, footer => [{prog=>"<b>".$cnt." ���.</b>", fio_teacher=>"<b>���-��:</b>"}]});

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
elsif (defined($fio) && length($fio)!=0) #���� ��� ����������, �������� � ��� �� ����� 0, �� ��������� �����
{
my $cnt=0;
my @result;

my $cgi=CGI->new;
my $data;
my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1="select pupils.Num_dogovor as nm_dg, pupils.FIO as fio_student, teachers.FIO as fio_teacher, kind_programm.NAME_PROGRAMM as prog, branches.BRANCH as br from pupils, pays, groups, kind_programm, lessons, teachers, branches where pupils.Num_dogovor=pays.PUPILS_NUM_DOGOVOR and pays.GROUP_ID=groups.ID and kind_programm.ID=groups.KIND_PROGRAMM and lessons.GROUP_ID=groups.ID and lessons.TEACHER_ID=teachers.ID and pupils.BRANCH=branches.ID and pupils.FIO like ? group by pupils.FIO order by pupils.FIO";
$sth1=$dbh1->prepare($sql1);
$sth1->execute('%'.$fio.'%');
#� ������ ���������� ����������� ������
while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
$cnt++;
}

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, footer => [{prog=>"<b>".$cnt." ���.</b>", fio_teacher=>"<b>���-��:</b>"}]});

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
elsif (defined($n_dogovor) && length($n_dogovor)!=0)
{
my $cnt=0;
my @result;

my $cgi=CGI->new;
my $data;
#������� ������ �� ������� ��������� � ������� ���� ������ ��������
my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1="select pupils.Num_dogovor as nm_dg, pupils.FIO as fio_student, teachers.FIO as fio_teacher, kind_programm.NAME_PROGRAMM as prog, branches.BRANCH as br from pupils, pays, groups, kind_programm, lessons, teachers, branches where pupils.Num_dogovor=pays.PUPILS_NUM_DOGOVOR and pays.GROUP_ID=groups.ID and kind_programm.ID=groups.KIND_PROGRAMM and lessons.GROUP_ID=groups.ID and lessons.TEACHER_ID=teachers.ID and pupils.BRANCH=branches.ID and pupils.Num_dogovor=? group by pupils.FIO order by pupils.FIO";
$sth1=$dbh1->prepare($sql1);
$sth1->execute($n_dogovor);
#� ������ ���������� ����������� ������
while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
$cnt++;
}

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, footer => [{prog=>"<b>".$cnt." ���.</b>", fio_teacher=>"<b>���-��:</b>"}]});

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
elsif (defined($programm) && length($programm)!=0)
{
my $cnt=0;
my @result;

my $cgi=CGI->new;
my $data;
my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1="select pupils.Num_dogovor as nm_dg, pupils.FIO as fio_student, teachers.FIO as fio_teacher, kind_programm.NAME_PROGRAMM as prog, branches.BRANCH as br from pupils, pays, groups, kind_programm, lessons, teachers, branches where pupils.Num_dogovor=pays.PUPILS_NUM_DOGOVOR and pays.GROUP_ID=groups.ID and kind_programm.ID=groups.KIND_PROGRAMM and lessons.GROUP_ID=groups.ID and lessons.TEACHER_ID=teachers.ID and pupils.BRANCH=branches.ID and kind_programm.ID=? group by pupils.FIO order by pupils.FIO";
$sth1=$dbh1->prepare($sql1);
$sth1->execute($programm);
#� ������ ���������� ����������� ������
while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
$cnt++;
}

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, footer => [{prog=>"<b>".$cnt." ���.</b>", fio_teacher=>"<b>���-��:</b>"}]});

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
elsif (defined($branch) && length($branch)!=0)
{
my $cnt=0;
my @result;

my $cgi=CGI->new;
my $data;
my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1="select pupils.Num_dogovor as nm_dg, pupils.FIO as fio_student, teachers.FIO as fio_teacher, kind_programm.NAME_PROGRAMM as prog, branches.BRANCH as br from pupils, pays, groups, kind_programm, lessons, teachers, branches where pupils.Num_dogovor=pays.PUPILS_NUM_DOGOVOR and pays.GROUP_ID=groups.ID and kind_programm.ID=groups.KIND_PROGRAMM and lessons.GROUP_ID=groups.ID and lessons.TEACHER_ID=teachers.ID and pupils.BRANCH=branches.ID and pupils.BRANCH=? group by pupils.FIO order by pupils.FIO";
$sth1=$dbh1->prepare($sql1);
$sth1->execute($branch);
#� ������ ���������� ����������� ������
while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
$cnt++;
}

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, footer => [{prog=>"<b>".$cnt." ���.</b>", fio_teacher=>"<b>���-��:</b>"}]});

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");

print $json;
exit();
}
else #����� ��� �� ����������, �� �������� � ��� ����� 0, �� ���������� ���� ������ ���������
{
my $cnt=0;
my @result;

my $cgi=CGI->new;
my $data;
my $dbh1=ConnectDB->connect; #���������� ������ ConnectDB ��� ����������� � ��
my $sth1=$dbh1->do("SET NAMES 'cp1251'");
my $sql1="select pupils.Num_dogovor as nm_dg, pupils.FIO as fio_student, teachers.FIO as fio_teacher, kind_programm.NAME_PROGRAMM as prog, branches.BRANCH as br from pupils, pays, groups, kind_programm, lessons, teachers, branches where pupils.Num_dogovor=pays.PUPILS_NUM_DOGOVOR and pays.GROUP_ID=groups.ID and kind_programm.ID=groups.KIND_PROGRAMM and lessons.GROUP_ID=groups.ID and lessons.TEACHER_ID=teachers.ID and pupils.BRANCH=branches.ID group by pupils.FIO order by pupils.FIO";
$sth1=$dbh1->prepare($sql1);
$sth1->execute();
#� ������ ���������� ����������� ������
while ($data=$sth1->fetchrow_hashref) {
push @result, $data;
$cnt++;
}

my $op=JSON::XS->new->pretty(1);
my $json=$op->encode({ rows=> \@result, footer => [{prog=>"<b>".$cnt." ���.</b>", fio_teacher=>"<b>���-��:</b>"}]});

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