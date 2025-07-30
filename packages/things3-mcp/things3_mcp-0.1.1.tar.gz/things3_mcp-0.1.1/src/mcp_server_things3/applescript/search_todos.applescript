use framework "Foundation"
use scripting additions

on todo_to_dict(theTodo)
    set theDict to current application's NSMutableDictionary's dictionary()
    
    tell application "Things3"
        theDict's setValue:(id of theTodo) forKey:"id"
        theDict's setValue:(name of theTodo) forKey:"title"
        
        if notes of theTodo is not missing value then
            theDict's setValue:(notes of theTodo) forKey:"notes"
        else
            theDict's setValue:"" forKey:"notes"
        end if
        
        if due date of theTodo is not missing value then
            theDict's setValue:((due date of theTodo) as string) forKey:"due_date"
        else
            theDict's setValue:"" forKey:"due_date"
        end if
        
        if activation date of theTodo is not missing value then
            theDict's setValue:((activation date of theTodo) as string) forKey:"when"
        else
            theDict's setValue:"" forKey:"when"
        end if
        
        -- Get status
        set taskStatus to status of theTodo as string
        theDict's setValue:taskStatus forKey:"status"
        
        set tagList to tag names of theTodo
        if tagList is not {} then
            set AppleScript's text item delimiters to ","
            set tagText to tagList as string
            set AppleScript's text item delimiters to ""
            theDict's setValue:tagText forKey:"tags"
        else
            theDict's setValue:"" forKey:"tags"
        end if
    end tell
    
    return theDict
end todo_to_dict

on search_and_convert(searchQuery)
    set matchingTodos to current application's NSMutableArray's array()
    
    tell application "Things3"
        set allTodos to to dos
        
        repeat with aTodo in allTodos
            set taskTitle to name of aTodo
            set taskNotes to ""
            if notes of aTodo is not missing value then
                set taskNotes to notes of aTodo
            end if
            
            -- Check if query matches title or notes
            if taskTitle contains searchQuery or taskNotes contains searchQuery then
                set todoDict to my todo_to_dict(aTodo)
                matchingTodos's addObject:todoDict
            end if
        end repeat
    end tell
    
    set {jsonData, theError} to current application's NSJSONSerialization's dataWithJSONObject:matchingTodos options:0 |error|:(reference)
    
    if jsonData is missing value then
        error (theError's localizedDescription() as text)
    end if
    
    set jsonString to current application's NSString's alloc()'s initWithData:jsonData encoding:(current application's NSUTF8StringEncoding)
    
    return jsonString as text
end search_and_convert

-- The search query will be passed as a command line argument
on run argv
    if (count of argv) is 0 then
        return "[]"
    else
        set searchQuery to item 1 of argv
        return search_and_convert(searchQuery)
    end if
end run