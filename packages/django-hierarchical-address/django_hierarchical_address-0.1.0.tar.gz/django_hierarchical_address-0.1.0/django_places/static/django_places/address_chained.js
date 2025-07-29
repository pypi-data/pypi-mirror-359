(function($) {
    $(document).ready(function() {
        function updateOptions($select, data, emptyLabel) {
            $select.empty();
            $select.append($('<option>', {value: '', text: emptyLabel}));
            $.each(data, function(i, obj) {
                $select.append($('<option>', {value: obj.id, text: obj.name}));
            });
        }

        function fetchAndUpdate(url, $select, emptyLabel) {
            $.get(url, function(response) {
                updateOptions($select, response.results, emptyLabel);
            });
        }

        var $country = $('#id_country');
        var $state = $('#id_state_province');
        var $city = $('#id_city');
        var $county = $('#id_county');

        $country.change(function() {
            var countryId = $(this).val();
            if (countryId) {
                fetchAndUpdate('/api/places/states-provinces/?country=' + countryId, $state, '---------');
            } else {
                updateOptions($state, [], '---------');
            }
            updateOptions($city, [], '---------');
            updateOptions($county, [], '---------');
        });

        $state.change(function() {
            var stateId = $(this).val();
            if (stateId) {
                fetchAndUpdate('/api/places/cities/?state_province=' + stateId, $city, '---------');
            } else {
                updateOptions($city, [], '---------');
            }
            updateOptions($county, [], '---------');
        });

        $city.change(function() {
            var cityId = $(this).val();
            if (cityId) {
                fetchAndUpdate('/api/places/counties/?city=' + cityId, $county, '---------');
            } else {
                updateOptions($county, [], '---------');
            }
        });
    });
})(django.jQuery); 