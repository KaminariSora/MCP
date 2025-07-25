#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ErrorCode,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  McpError,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// Todo item interface
interface TodoItem {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  createdAt: string;
}

// In-memory storage for todos
let todos: TodoItem[] = [
  {
    id: "1",
    title: "เรียนรู้ MCP",
    description: "ศึกษา Model Context Protocol และวิธีการใช้งาน",
    completed: false,
    createdAt: new Date().toISOString(),
  },
  {
    id: "2", 
    title: "สร้างโปรเจคตัวอย่าง",
    description: "พัฒนาแอปพลิเคชัน Todo ด้วย MCP",
    completed: true,
    createdAt: new Date().toISOString(),
  },
];

class TodoServer {
  private server: Server;

  constructor() {
    this.server = new Server({
      name: "todo-server",
      version: "0.1.0",
      capabilities: {
        resources: {},
        tools: {},
      },
    });

    this.setupToolHandlers();
    this.setupResourceHandlers();
  }

  private setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: "add_todo",
            description: "เพิ่มรายการงานใหม่",
            inputSchema: {
              type: "object",
              properties: {
                title: {
                  type: "string",
                  description: "หัวข้องาน",
                },
                description: {
                  type: "string", 
                  description: "รายละเอียดงาน (ไม่บังคับ)",
                },
              },
              required: ["title"],
            },
          },
          {
            name: "list_todos",
            description: "แสดงรายการงานทั้งหมด",
            inputSchema: {
              type: "object",
              properties: {
                filter: {
                  type: "string",
                  enum: ["all", "completed", "pending"],
                  description: "กรองรายการงาน",
                  default: "all",
                },
              },
            },
          },
          {
            name: "complete_todo", 
            description: "ทำเครื่องหมายงานเสร็จสิ้น",
            inputSchema: {
              type: "object",
              properties: {
                id: {
                  type: "string",
                  description: "ID ของงาน",
                },
              },
              required: ["id"],
            },
          },
          {
            name: "delete_todo",
            description: "ลบรายการงาน",
            inputSchema: {
              type: "object", 
              properties: {
                id: {
                  type: "string",
                  description: "ID ของงาน",
                },
              },
              required: ["id"],
            },
          },
        ],
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case "add_todo":
            return await this.addTodo(args as { title: string; description?: string });
          
          case "list_todos":
            return await this.listTodos(args as { filter?: "all" | "completed" | "pending" });
          
          case "complete_todo":
            return await this.completeTodo(args as { id: string });
          
          case "delete_todo":
            return await this.deleteTodo(args as { id: string });

          default:
            throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        return {
          content: [
            {
              type: "text",
              text: `Error: ${errorMessage}`,
            },
          ],
        };
      }
    });
  }

  private setupResourceHandlers() {
    // List resources
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => {
      return {
        resources: [
          {
            uri: "todo://all",
            mimeType: "application/json", 
            name: "รายการงานทั้งหมด",
            description: "ข้อมูลรายการงานทั้งหมดในรูปแบบ JSON",
          },
        ],
      };
    });

    // Read resource
    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const { uri } = request.params;

      if (uri === "todo://all") {
        return {
          contents: [
            {
              uri,
              mimeType: "application/json",
              text: JSON.stringify(todos, null, 2),
            },
          ],
        };
      }

      throw new McpError(ErrorCode.InvalidRequest, `Unknown resource: ${uri}`);
    });
  }

  // Tool implementations
  private async addTodo(args: { title: string; description?: string }) {
    const newTodo: TodoItem = {
      id: (todos.length + 1).toString(),
      title: args.title,
      description: args.description,
      completed: false,
      createdAt: new Date().toISOString(),
    };

    todos.push(newTodo);

    return {
      content: [
        {
          type: "text", 
          text: `เพิ่มงาน "${newTodo.title}" เรียบร้อยแล้ว (ID: ${newTodo.id})`,
        },
      ],
    };
  }

  private async listTodos(args: { filter?: "all" | "completed" | "pending" }) {
    const filter = args.filter || "all";
    let filteredTodos = todos;

    if (filter === "completed") {
      filteredTodos = todos.filter(todo => todo.completed);
    } else if (filter === "pending") {
      filteredTodos = todos.filter(todo => !todo.completed);
    }

    const todoList = filteredTodos
      .map(todo => 
        `${todo.completed ? "✅" : "⏳"} [${todo.id}] ${todo.title}` +
        (todo.description ? `\n   📝 ${todo.description}` : "")
      )
      .join("\n\n");

    return {
      content: [
        {
          type: "text",
          text: `รายการงาน (${filter}):\n\n${todoList || "ไม่มีรายการงาน"}`,
        },
      ],
    };
  }

  private async completeTodo(args: { id: string }) {
    const todoIndex = todos.findIndex(todo => todo.id === args.id);
    
    if (todoIndex === -1) {
      throw new Error(`ไม่พบงานที่มี ID: ${args.id}`);
    }

    todos[todoIndex].completed = true;

    return {
      content: [
        {
          type: "text",
          text: `ทำเครื่องหมายงาน "${todos[todoIndex].title}" เสร็จสิ้นแล้ว`,
        },
      ],
    };
  }

  private async deleteTodo(args: { id: string }) {
    const todoIndex = todos.findIndex(todo => todo.id === args.id);
    
    if (todoIndex === -1) {
      throw new Error(`ไม่พบงานที่มี ID: ${args.id}`);
    }

    const deletedTodo = todos.splice(todoIndex, 1)[0];

    return {
      content: [
        {
          type: "text",
          text: `ลบงาน "${deletedTodo.title}" เรียบร้อยแล้ว`,
        },
      ],
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("Todo MCP server running on stdio");
  }
}

// Start the server
const server = new TodoServer();
server.run().catch(console.error);