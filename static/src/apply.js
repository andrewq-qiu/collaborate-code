/*This file contains the apply function,
which helps apply operations onto the Ace
Editor


Copyright and Usage Information
===============================

This project and file is licensed with the MIT License.
See https://github.com/andrewcoool/collaborate-code/
and the LICENSE file for more information.

Author: Andrew Qiu (GitHub @andrewcoool)
*/

/**
 * Apply an operation to the Ace Editor.
 * @param {Array} op - the operation to be applied
 * @param {Editor} editor_ - the ace editor to apply the operation on
 */
function apply(op, editor_){
    if (op[0] == 'ID'){return;}

    // Default row 0 for now
    const pos = {'row': op[1][0], 'column': op[1][1]};

    if (op[0] == 'INS'){

        editor_.session.insert(pos, op[2]);
    }else if (op[0] == 'DEL'){
        // const range = new ace.require('ace/range').Range(0, op[1], 0, op[1] + 1);
        // console.log(range);

        if (pos['column'] == -1){
            const range = {
                'start': {'row': pos['row'] - 1, 'column': editor_.session.getLine(pos['row'] - 1).length},
                'end': {'row': pos['row'], 'column': 0}
            }

            console.log(range);

            editor_.session.remove(range);
        }else{
            const range = {
                'start': {'row': pos['row'], 'column': pos['column']},
                'end': {'row': pos['row'], 'column': pos['column'] + 1}
            }

            editor_.session.remove(range);
        }
        
    }
    
}