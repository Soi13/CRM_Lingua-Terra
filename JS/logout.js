function confirm1(){
        $.messager.confirm('��������!', '�� �������, ��� ���������� �����?', function(r){
        if (r){
        //alert('confirmed: '+r);
        window.location.replace("/cgi-bin/exit.cgi?SID=$SID");
              }
          }); 
       }   