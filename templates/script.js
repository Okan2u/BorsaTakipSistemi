$(document).ready(function() {
    function getFiyat() {
        $.ajax({
            url: "/fiyat_güncelle",
            type: "GET",
            success: function(response) {
                var yeniFiyat = response.dolar_detaylari;
                var eskiFiyat = $('#dolar_detaylari').text();

                // Eski fiyat yoksa veya fiyat değiştiyse
                if (!eskiFiyat || yeniFiyat !== eskiFiyat) {
                    // Yeni fiyatı HTML elementine güncelle
                    $('#dolar_detaylari').text(yeniFiyat);

                    // Navbar içindeki dolar linkini güncelle
                    $('#dolar_link').text('Dolar: ' + yeniFiyat);

                    // Eski fiyat yoksa veya fiyat arttıysa yeşil, azaldıysa kırmızı renk kullan
                    if (!eskiFiyat || parseFloat(yeniFiyat) > parseFloat(eskiFiyat)) {
                        $('#dolar_detaylari').css('color', 'green');
                        $('#dolar_link').css('color', 'green');
                    } else {
                        $('#dolar_detaylari').css('color', 'red');
                        $('#dolar_link').css('color', 'red');
                    }
                }
            },
            error: function(xhr) {
                console.log(xhr.responseText);
            }
        });
    }

    getFiyat();
    setInterval(getFiyat, 3000);
});
