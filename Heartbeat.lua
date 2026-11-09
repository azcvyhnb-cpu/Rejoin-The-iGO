-- File: Heartbeat.lua (theIGO Ultimate Edition)
if not game:IsLoaded() then
    game.Loaded:Wait()
end

local Players = game:GetService("Players")
local GuiService = game:GetService("GuiService")
local CoreGui = game:GetService("CoreGui")
local VirtualUser = game:GetService("VirtualUser")
local HttpService = game:GetService("HttpService")

local LocalPlayer = Players.LocalPlayer
while not LocalPlayer do
    task.wait(0.5)
    LocalPlayer = Players.LocalPlayer
end

local HB_FILE = "heartbeat.json"
local isDead = false

-- ระบบ Anti-AFK ป้องกันหลุดเมื่อยืนนิ่งครบ 20 นาที
LocalPlayer.Idled:Connect(function()
    pcall(function()
        VirtualUser:CaptureController()
        VirtualUser:ClickButton2(Vector2.new())
    end)
end)

-- ตรวจสอบหน้าต่างแจ้งเตือน Error ทุกชนิด (รวมถึง Error Code: 524, 277, 267)
local function checkErrorPrompt()
    local code = GuiService:GetErrorCode().Value
    if code ~= 0 then
        return true, "ErrorCode_" .. tostring(code)
    end

    local promptGui = CoreGui:FindFirstChild("RobloxPromptGui")
    if promptGui then
        local overlay = promptGui:FindFirstChild("promptOverlay")
        if overlay then
            local errPrompt = overlay:FindFirstChild("ErrorPrompt")
            if errPrompt and errPrompt.Visible then
                return true, "ErrorPrompt_Visible"
            end
        end
    end
    return false, "OK"
end

-- เขียนไฟล์ส่งสัญญาณชีพให้ rejoin.py
local function writeHeartbeat(statusStr)
    pcall(function()
        local data = {
            timestamp = os.time(),
            status = statusStr,
            placeId = game.PlaceId,
            jobId = game.JobId
        }
        writefile(HB_FILE, HttpService:JSONEncode(data))
    end)
end

writeHeartbeat("ALIVE")

GuiService.ErrorMessageChanged:Connect(function(msg)
    if msg and msg ~= "" then
        isDead = true
        writeHeartbeat("ERROR: " .. tostring(msg))
    end
end)

task.spawn(function()
    while not isDead do
        local hasErr, errReason = checkErrorPrompt()
        if hasErr then
            isDead = true
            writeHeartbeat("ERROR: " .. errReason)
            break
        end
        writeHeartbeat("ALIVE")
        task.wait(3)
    end
end)
