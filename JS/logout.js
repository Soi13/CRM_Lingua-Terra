function confirm1(){
        $.messager.confirm('Внимание!', 'Вы уверены, что необходимо выйти?', function(r){
        if (r){
        //alert('confirmed: '+r);
        window.location.replace("/cgi-bin/exit.cgi?SID=$SID");
              }
          }); 
       }   