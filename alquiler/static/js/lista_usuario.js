$(document).ready(function() {
    $('[title]').tooltip({
        trigger: 'hover',
        placement: 'top',
        container: 'body'
    });
    
    $('#estadoFilter, #rolFilter').change(function() {
        $(this).closest('form').submit();
    });
    
    $('.users-table tbody tr').hover(
        function() {
            $(this).css('transform', 'translateX(2px)');
        },
        function() {
            $(this).css('transform', 'translateX(0)');
        }
    );
    
    $('.action-button').hover(
        function() {
            $(this).css('transform', 'scale(1.1)');
        },
        function() {
            $(this).css('transform', 'scale(1)');
        }
    );
    
    $('.action-button.delete').click(function(e) {
        if (!confirm('¿Estás seguro que deseas eliminar este usuario?')) {
            e.preventDefault();
            return false;
        }
    });
});
