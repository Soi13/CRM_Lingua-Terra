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

#Если сессия пустая
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#Если вермя сессии истекло
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#Если IP не совпадают
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#Присваиваем переменным логин и пароль пользователя из сессии
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');

#Смотрим определены ли логин и пароль пользователя в сесии
if (defined($formLogin) && defined($formPass)) {

my $num_dog=param('num_dog');
$num_dog=~s/\0//g; $num_dog=~s/\.\.//g; $num_dog=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;

my $cgi=CGI->new;
my @res;

my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
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
my $sth11=$dbh->do("SET NAMES 'cp1251'");
my $sth17=$dbh->do("SET NAMES 'cp1251'");
my $sth21=$dbh->do("SET NAMES 'cp1251'");
my $sth24=$dbh->do("SET NAMES 'cp1251'");
my $sth25=$dbh->do("SET NAMES 'cp1251'");
my $sth26=$dbh->do("SET NAMES 'cp1251'");
my $sth27=$dbh->do("SET NAMES 'cp1251'");
my $sth28=$dbh->do("SET NAMES 'cp1251'");
my $sth29=$dbh->do("SET NAMES 'cp1251'");
my $sth30=$dbh->do("SET NAMES 'cp1251'");
my $sth31=$dbh->do("SET NAMES 'cp1251'");
my $sth32=$dbh->do("SET NAMES 'cp1251'");
my $sth33=$dbh->do("SET NAMES 'cp1251'");
my $sth34=$dbh->do("SET NAMES 'cp1251'");
my $sth35=$dbh->do("SET NAMES 'cp1251'");
my $sth36=$dbh->do("SET NAMES 'cp1251'");


my $sql="select 'Дата рождения' as 'name', date(DATE_OF_BORN) as 'value', 'Личные данные' as 'group' from pupils where Num_dogovor like ?";
my $sql1="select 'Серия паспорта' as 'name', PASSPORT as 'value', 'Личные данные' as 'group' from pupils where Num_dogovor like ?";
my $sql2="select 'Номер паспорта' as 'name', PASSPORT_NUM as 'value', 'Личные данные' as 'group' from pupils where Num_dogovor like ?";
my $sql3="select 'Кем выдан' as 'name', PASSPORT_VIDAN as 'value', 'Личные данные' as 'group' from pupils where Num_dogovor like ?";
my $sql4="select 'Когда выдан' as 'name', date(PASSPORT_DATE) as 'value', 'Личные данные' as 'group' from pupils where Num_dogovor like ?";
my $sql5="select 'Пол' as 'name', SEX as 'value', 'Личные данные' as 'group' from pupils where Num_dogovor like ?";
my $sql6="select 'Дом. адрес' as 'name', HOME_ADDRESS as 'value', 'Контактная информация' as 'group' from pupils where Num_dogovor like ?";
my $sql7="select 'Раб. тел.' as 'name', WORK_PHONE as 'value', 'Контактная информация' as 'group' from pupils where Num_dogovor like ?";
my $sql8="select 'Моб.тел.ребенка' as 'name', MOBILE_CHILD as 'value', 'Контактная информация' as 'group' from pupils where Num_dogovor like ?";
my $sql9="select 'E-Mail' as 'name', EMAIL as 'value', 'Контактная информация' as 'group' from pupils where Num_dogovor like ?";
my $sql10="select 'Место работы/учебы' as 'name', PLACE_OF_WORK as 'value', 'Контактная информация' as 'group' from pupils where Num_dogovor like ?";
my $sql11="select 'Должность/факультет' as 'name', POSITION_FACULT as 'value', 'Контактная информация' as 'group' from pupils where Num_dogovor like ?";
my $sql17="select 'Филиал' as 'name', branches.BRANCH as 'value', 'Информация по обучению' as 'group' from pupils, branches where pupils.BRANCH=branches.ID and pupils.Num_dogovor like ?";
my $sql21="select 'Дата заполнения' as 'name', date(DATE_OF_FILLING) as 'value', 'Информация по заполнению' as 'group' from pupils where Num_dogovor like ?";
my $sql24="select 'Откуда о нас узнали' as 'name', source_about_us.SOURCE as 'value', 'Другое' as 'group' from pupils, source_about_us where pupils.SOURCE_ABOUT_US=source_about_us.ID and pupils.Num_dogovor like ?";
my $sql25="select 'ФИО' as 'name', FIO_PARENT as 'value', 'Информация о родителе' as 'group' from pupils where Num_dogovor like ?";
my $sql26="select 'Номер паспорта' as 'name', NUM_PASSPORT_PARENT as 'value', 'Информация о родителе' as 'group' from pupils where Num_dogovor like ?";
my $sql27="select 'Серия паспорта' as 'name', SER_PASSPORT_PARENT as 'value', 'Информация о родителе' as 'group' from pupils where Num_dogovor like ?";
my $sql28="select 'Кем выдан' as 'name', KEM_VIDANO_PASSPORT_PARENT as 'value', 'Информация о родителе' as 'group' from pupils where Num_dogovor like ?";
my $sql29="select 'Когда выдан' as 'name', KOGDA_VIDANO_PASSPORT_PARENT as 'value', 'Информация о родителе' as 'group' from pupils where Num_dogovor like ?";
my $sql33="select 'Примечания' as 'name', STUDENT_INTERESTS as 'value', 'Дополнительная информация' as 'group' from pupils where Num_dogovor like ?";
my $sql34="select 'Обучение по бартеру' as 'name', IF(BARTER=1,'Да','Нет') as 'value', 'Дополнительная информация' as 'group' from pupils where Num_dogovor like ?";
my $sql35="select 'Индивидуальное обучение' as 'name', IF(INDIVIDUAL=1,'Да','Нет') as 'value', 'Дополнительная информация' as 'group' from pupils where Num_dogovor like ?";
my $sql36="select 'Временный пароль' as 'name', TEMP_PASSW as 'value', 'Дополнительная информация' as 'group' from pupils where Num_dogovor like ?";
my $sql30="select 'Согласие на получение SMS' as 'name', IF(AGREMMENT_GET_SMS=1,'Да','Нет') as 'value', 'Информация о согласиях' as 'group' from pupils where Num_dogovor like ?";
my $sql31="select 'Согласие на получение E-mail' as 'name', IF(AGREMMENT_GET_EMAIL=1,'Да','Нет') as 'value', 'Информация о согласиях' as 'group' from pupils where Num_dogovor like ?";
my $sql32="select 'Согласие на использование ФОТО' as 'name', IF(AGREMMENT_USE_PHOTO=1,'Да','Нет') as 'value', 'Информация о согласиях' as 'group' from pupils where Num_dogovor like ?";


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
$sth11=$dbh->prepare($sql11);
$sth17=$dbh->prepare($sql17);
$sth21=$dbh->prepare($sql21);
$sth24=$dbh->prepare($sql24);
$sth25=$dbh->prepare($sql25);
$sth26=$dbh->prepare($sql26);
$sth27=$dbh->prepare($sql27);
$sth28=$dbh->prepare($sql28);
$sth29=$dbh->prepare($sql29);
$sth30=$dbh->prepare($sql30);
$sth31=$dbh->prepare($sql31);
$sth32=$dbh->prepare($sql32);
$sth33=$dbh->prepare($sql33);
$sth34=$dbh->prepare($sql34);
$sth35=$dbh->prepare($sql35);
$sth36=$dbh->prepare($sql36);

$sth->execute($num_dog);
$sth1->execute($num_dog);
$sth2->execute($num_dog);
$sth3->execute($num_dog);
$sth4->execute($num_dog);
$sth5->execute($num_dog);
$sth6->execute($num_dog);
$sth7->execute($num_dog);
$sth8->execute($num_dog);
$sth9->execute($num_dog);
$sth10->execute($num_dog);
$sth11->execute($num_dog);
$sth17->execute($num_dog);
$sth21->execute($num_dog);
$sth24->execute($num_dog);
$sth25->execute($num_dog);
$sth26->execute($num_dog);
$sth27->execute($num_dog);
$sth28->execute($num_dog);
$sth29->execute($num_dog);
$sth30->execute($num_dog);
$sth31->execute($num_dog);
$sth32->execute($num_dog);
$sth33->execute($num_dog);
$sth34->execute($num_dog);
$sth35->execute($num_dog);
$sth36->execute($num_dog);

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
while ($data=$sth11->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth17->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth21->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth24->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth25->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth26->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth27->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth28->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth29->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth33->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth34->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth35->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth36->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth30->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth31->fetchrow_hashref) {
push @res, $data;
}
while ($data=$sth32->fetchrow_hashref) {
push @res, $data;
}
$dbh->disconnect;

my $op=JSON->new->pretty(1);
my $json=$op->encode({ rows=> \@res, total => 4 });

print $cgi->header(-type=>"applicayion/json", -charset=>"windows-1251");
print $json;

#Удаление сессии
sub f_delete_session {
         #Удаляем куки
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'https://linguaterra-soft.ru');
         print "Set-Cookie: $cookies\n";
         #Удаляем сессию
         $sess->delete();
         $sess->flush();
        }

#Добавление SID к URL-адресу
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