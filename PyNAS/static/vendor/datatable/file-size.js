/**
 * When dealing with computer file sizes, it is common to append a post fix
 * such as B, KB, MB or GB to a string in order to easily denote the order of
 * magnitude of the file size. This plug-in allows sorting to take these
 * indicates of size into account.
 *
 * A counterpart type detection plug-in is also available.
 *
 *  @name File size
 *  @summary Sort abbreviated file sizes correctly (8MB, 4KB, etc)
 *  @author Allan Jardine - datatables.net
 *
 *  @example
 *    $('#example').DataTable( {
 *       columnDefs: [
 *         { type: 'file-size', targets: 0 }
 *       ]
 *    } );
 */

jQuery.fn.dataTable.ext.type.order['file-size-pre'] = function ( data ) {
    var matches = data.match( /^(\d+(?:\.\d+)?)\s*([a-z]+)/i );
    var multipliers = {
        B:  1,
        Bytes: 1,
        KB: 1000,
        KiB: 1024,
        MB: 1000000,
        MiB: 1048576,
        GB: 1000000000,
        GiB: 1073741824,
        TB: 1000000000000,
        TiB: 1099511627776,
        PB: 1000000000000000,
        PiB: 1125899906842624
    };

    if (matches) {
        var multiplier = multipliers[matches[2].toLowerCase()];
        return parseFloat( matches[1] ) * multiplier;
    } else {
        return -1;
    };
};
